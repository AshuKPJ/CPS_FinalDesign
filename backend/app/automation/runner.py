# backend/app/automation/runner.py

import asyncio
import csv
import io
import uuid
from typing import List
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from app.utils.logger import log_event
from app.automation.browser_utils import launch_browser, close_browser, open_page
from app.automation.form_detector import detect_form_on_page
from app.automation.field_mapper import map_fields_and_fill
from app.db.models.campaign import Campaign
from app.db.models.user_contact_profile import UserContactProfile
from app.db.models.website import Website
from app.db.models.submission import Submission
from playwright.async_api import async_playwright

def run_campaign_automation(file, proxy: str, halt_on_captcha: bool, user_id: str, db: Session):
    # Step 1: Parse CSV and extract websites
    contents = file.file.read().decode("utf-8")
    file.file.close()
    df = pd.read_csv(io.StringIO(contents))

    if 'website' not in df.columns and 'Website' not in df.columns:
        raise ValueError("CSV must contain a 'website' or 'Website' column.")

    website_column = 'website' if 'website' in df.columns else 'Website'
    websites = df[website_column].dropna().unique().tolist()

    # Step 2: Create campaign record
    campaign = Campaign(
        id=uuid.uuid4(),
        user_id=user_id,
        name=f"Campaign {datetime.utcnow().isoformat()[:19]}",
        csv_filename=file.filename,
        started_at=datetime.utcnow(),
        status="processing"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    campaign_id = str(campaign.id)
    log_event(db, user_id, "Campaign and CSV parsed. Starting automation...", campaign_id=campaign_id)

    # Step 3: Begin async processing
    asyncio.run(run_campaign_automation_async(websites, proxy, halt_on_captcha, user_id, campaign_id, db))


async def run_campaign_automation_async(websites: List[str], proxy: str, halt_on_captcha: bool, user_id: str, campaign_id: str, db: Session):
    from app.db.models.user_contact_profile import UserContactProfile
    from app.db.models.website import Website
    from app.db.models.submission import Submission

    log_event(db, user_id, "Automation started.", campaign_id=campaign_id)

    async with async_playwright() as p:
        browser = await launch_browser(p, proxy)

        for index, domain in enumerate(websites):
            try:
                log_event(db, user_id, f"Opening site #{index+1}: {domain}", campaign_id=campaign_id)

                page = await open_page(browser, domain)
                if not page:
                    log_event(db, user_id, f"❌ Failed to open {domain}", campaign_id=campaign_id)
                    continue

                form_info = await detect_form_on_page(page)
                website_id = uuid.uuid4()

                website = Website(
                    id=website_id,
                    campaign_id=campaign_id,
                    domain=domain,
                    user_id=user_id,
                    form_detected=bool(form_info),
                    status="form_detected" if form_info else "no_form",
                    created_at=datetime.utcnow()
                )
                db.add(website)
                db.commit()

                if form_info:
                    log_event(db, user_id, f"Form detected on {domain} with fields: {form_info['fields']}", campaign_id=campaign_id, website_id=website_id)

                    profile = db.query(UserContactProfile).filter_by(user_id=user_id).first()
                    if not profile:
                        log_event(db, user_id, f"⚠️ User contact profile missing.", campaign_id=campaign_id, website_id=website_id)
                        continue

                    await map_fields_and_fill(page, form_info['fields'], profile)

                    if form_info['has_captcha']:
                        log_event(db, user_id, f"🛑 CAPTCHA found on {domain}", campaign_id=campaign_id, website_id=website_id)
                        if halt_on_captcha:
                            log_event(db, user_id, "Halting due to CAPTCHA", campaign_id=campaign_id, website_id=website_id)
                            break

                    await page.click(form_info['submit_selector'])
                    log_event(db, user_id, f"✅ Submitted form on {domain}", campaign_id=campaign_id, website_id=website_id)

                    submission = Submission(
                        id=uuid.uuid4(),
                        website_id=website_id,
                        user_id=user_id,
                        success=True,
                        submitted_at=datetime.utcnow(),
                        form_fields_sent={"fields": form_info['fields']},
                        response_status=200
                    )
                    db.add(submission)
                    db.commit()
                else:
                    log_event(db, user_id, f"❌ No form found on {domain}", campaign_id=campaign_id, website_id=website_id)

                await page.close()

            except Exception as e:
                log_event(db, user_id, f"🔥 Error processing {domain}: {str(e)}", campaign_id=campaign_id, level="ERROR")
                continue

        await close_browser(browser)
        log_event(db, user_id, "🎉 Automation finished.", campaign_id=campaign_id)
