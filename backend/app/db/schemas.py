from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, SecretStr

# ─────────────────────────────────────────────────────────────────────────────
# Auth / Tokens
# ─────────────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ─────────────────────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "user"
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    # Used by /auth/register
    password: str

class User(UserBase):
    id: UUID
    plan_id: Optional[UUID] = None
    subscription_status: Optional[str] = None
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    created_at: Optional[datetime] = None
    profile_image_url: Optional[str] = None
    class Config:
        from_attributes = True  # map from ORM

# ─────────────────────────────────────────────────────────────────────────────
# Campaigns
# ─────────────────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    # Your current endpoint posts name + websites (and optionally message_template)
    name: str
    websites: List[str] = []
    message_template: Optional[str] = None

class Campaign(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    name: Optional[str] = None
    csv_filename: Optional[str] = None
    started_at: Optional[datetime] = None
    status: Optional[str] = None
    class Config:
        from_attributes = True

# ─────────────────────────────────────────────────────────────────────────────
# Submissions (used by dashboards/joins; endpoint schema not required right now)
# ─────────────────────────────────────────────────────────────────────────────

class Submission(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    website_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    status: Optional[str] = None
    success: Optional[bool] = None
    response_status: Optional[int] = None
    submitted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    form_fields_sent: Optional[Dict[str, Any]] = None
    class Config:
        from_attributes = True

# ─────────────────────────────────────────────────────────────────────────────
# Submission Logs (dashboards)
# ─────────────────────────────────────────────────────────────────────────────

class SubmissionLog(BaseModel):
    id: UUID
    campaign_id: Optional[UUID] = None
    target_url: str
    status: Optional[str] = None
    details: Optional[str] = None
    processed_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# ─────────────────────────────────────────────────────────────────────────────
# Captcha settings (users.py)
# ─────────────────────────────────────────────────────────────────────────────

class CaptchaView(BaseModel):
    has_captcha: bool
    captcha_username: Optional[str] = None
    captcha_password: Optional[str] = None  # echoed back as plain for UI

class CaptchaUpdate(BaseModel):
    captcha_username: Optional[str] = None
    captcha_password: Optional[SecretStr] = None

# ─────────────────────────────────────────────────────────────────────────────
# User Contact Profile (user_contact_profile.py)
# ─────────────────────────────────────────────────────────────────────────────

class UserContactProfileOut(BaseModel):
    id: UUID
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    product_interest: Optional[str] = None
    budget_range: Optional[str] = None
    referral_source: Optional[str] = None
    preferred_contact: Optional[str] = None
    best_time_to_contact: Optional[str] = None
    is_existing_customer: Optional[bool] = None
    linkedin_url: Optional[str] = None
    language: Optional[str] = None
    preferred_language: Optional[str] = None
    notes: Optional[str] = None
    contact_source: Optional[str] = None
    form_custom_field_1: Optional[str] = None
    form_custom_field_2: Optional[str] = None
    form_custom_field_3: Optional[str] = None
    class Config:
        from_attributes = True

class UserContactProfileUpdate(BaseModel):
    # All fields optional for partial upsert
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    website_url: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    product_interest: Optional[str] = None
    budget_range: Optional[str] = None
    referral_source: Optional[str] = None
    preferred_contact: Optional[str] = None
    best_time_to_contact: Optional[str] = None
    is_existing_customer: Optional[bool] = None
    linkedin_url: Optional[str] = None
    language: Optional[str] = None
    preferred_language: Optional[str] = None
    notes: Optional[str] = None
    contact_source: Optional[str] = None
    form_custom_field_1: Optional[str] = None
    form_custom_field_2: Optional[str] = None
    form_custom_field_3: Optional[str] = None
