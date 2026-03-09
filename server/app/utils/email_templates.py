"""
HTML email templates matching the LabReport Interpreter app theme.
Colors: Deep Teal (#006D77), Warm Amber (#E29D3E), Off-White (#F4F7F9).
Typography: Poppins / Inter via Google Fonts.
"""


def _base_template(title: str, content: str, footer_text: str = "") -> str:
    """Wrap email content in the branded base layout."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body style="margin:0; padding:0; background-color:#F4F7F9; font-family:'Inter',Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F4F7F9; padding:40px 20px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#FFFFFF; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08);">
          
          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #006D77 0%, #004F59 100%); padding:32px 40px; text-align:center;">
              <h1 style="margin:0; font-family:'Poppins',sans-serif; font-size:24px; font-weight:700; color:#FFFFFF; letter-spacing:0.5px;">
                🔬 LabReport Interpreter
              </h1>
              <p style="margin:8px 0 0; font-family:'Inter',sans-serif; font-size:13px; color:rgba(255,255,255,0.8); letter-spacing:0.3px;">
                Understand your lab results
              </p>
            </td>
          </tr>
          
          <!-- Content -->
          <tr>
            <td style="padding:40px;">
              {content}
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="background-color:#F4F7F9; padding:24px 40px; text-align:center; border-top:1px solid #E5E7EB;">
              <p style="margin:0; font-size:12px; color:#6B7280; line-height:1.6;">
                {footer_text if footer_text else "This is an automated message from LabReport Interpreter.<br>Please do not reply to this email."}
              </p>
              <p style="margin:8px 0 0; font-size:11px; color:#9CA3AF;">
                &copy; 2026 LabReport Interpreter — Master's Project
              </p>
            </td>
          </tr>
          
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def otp_verification_email(name: str, otp_code: str) -> tuple[str, str]:
    """
    OTP verification email sent right after registration.

    Returns:
        Tuple of (subject, html_body).
    """
    subject = "Verify Your Email — LabReport Interpreter"
    content = f"""
    <h2 style="margin:0 0 8px; font-family:'Poppins',sans-serif; font-size:20px; color:#1A1A2E;">
      Verify Your Email Address
    </h2>
    <p style="margin:0 0 24px; font-size:15px; color:#6B7280; line-height:1.6;">
      Hi {name}, thanks for signing up! Please enter the code below in the app to verify your account.
    </p>
    
    <!-- OTP Code Box -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center" style="padding:24px 0;">
          <div style="display:inline-block; background:linear-gradient(135deg, #006D77 0%, #004F59 100%); border-radius:12px; padding:20px 48px;">
            <span style="font-family:'Poppins',monospace; font-size:36px; font-weight:700; color:#FFFFFF; letter-spacing:12px;">
              {otp_code}
            </span>
          </div>
        </td>
      </tr>
    </table>
    
    <p style="margin:24px 0 0; font-size:13px; color:#6B7280; line-height:1.6; text-align:center;">
      This code expires in <strong style="color:#E29D3E;">10 minutes</strong>.<br>
      If you didn't create an account, you can ignore this email.
    </p>"""
    
    return subject, _base_template("Verify Your Email", content)


def welcome_email(name: str) -> tuple[str, str]:
    """
    Welcome email sent after successful OTP verification.

    Returns:
        Tuple of (subject, html_body).
    """
    subject = "Welcome to LabReport Interpreter! 🎉"
    content = f"""
    <h2 style="margin:0 0 8px; font-family:'Poppins',sans-serif; font-size:20px; color:#1A1A2E;">
      Welcome, {name}! 🎉
    </h2>
    <p style="margin:0 0 24px; font-size:15px; color:#6B7280; line-height:1.6;">
      Your account has been verified and is ready to use. Here's what you can do:
    </p>
    
    <!-- Feature Cards -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        <td style="padding:16px; background-color:#F0FDFA; border-radius:10px; border-left:4px solid #006D77; margin-bottom:12px;">
          <strong style="color:#006D77; font-size:14px;">📄 Upload Lab Reports</strong>
          <p style="margin:4px 0 0; font-size:13px; color:#6B7280;">Upload a PDF or image, and we'll extract and analyze your results automatically.</p>
        </td>
      </tr>
      <tr><td style="height:12px;"></td></tr>
      <tr>
        <td style="padding:16px; background-color:#FFF7ED; border-radius:10px; border-left:4px solid #E29D3E;">
          <strong style="color:#E29D3E; font-size:14px;">📊 Track Trends</strong>
          <p style="margin:4px 0 0; font-size:13px; color:#6B7280;">Monitor how your lab values change over time with interactive charts.</p>
        </td>
      </tr>
      <tr><td style="height:12px;"></td></tr>
      <tr>
        <td style="padding:16px; background-color:#F0F9FF; border-radius:10px; border-left:4px solid #2ECC71;">
          <strong style="color:#2ECC71; font-size:14px;">🤖 ML-Powered Analysis</strong>
          <p style="margin:4px 0 0; font-size:13px; color:#6B7280;">Get plain-language summaries and condition predictions from our trained AI model.</p>
        </td>
      </tr>
    </table>
    
    <p style="margin:0; font-size:13px; color:#6B7280; text-align:center;">
      Open the app and upload your first lab report to get started! 🚀
    </p>"""
    
    return subject, _base_template("Welcome!", content)


def report_ready_email(
    name: str,
    report_date: str,
    total_tests: int,
    flagged_count: int,
    report_id: int,
) -> tuple[str, str]:
    """
    Notification email sent when a report has been processed.

    Returns:
        Tuple of (subject, html_body).
    """
    status_color = "#2ECC71" if flagged_count == 0 else "#E29D3E"
    status_text = "All Normal" if flagged_count == 0 else f"{flagged_count} Value(s) Flagged"
    status_emoji = "✅" if flagged_count == 0 else "⚠️"

    subject = f"Your Lab Report is Ready — {status_text}"
    content = f"""
    <h2 style="margin:0 0 8px; font-family:'Poppins',sans-serif; font-size:20px; color:#1A1A2E;">
      Your Report is Ready {status_emoji}
    </h2>
    <p style="margin:0 0 24px; font-size:15px; color:#6B7280; line-height:1.6;">
      Hi {name}, your lab report from <strong>{report_date}</strong> has been processed and analyzed.
    </p>
    
    <!-- Stats Cards -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        <td width="48%" style="padding:20px; background-color:#F0FDFA; border-radius:10px; text-align:center;">
          <p style="margin:0; font-size:28px; font-weight:700; color:#006D77; font-family:'Poppins',sans-serif;">{total_tests}</p>
          <p style="margin:4px 0 0; font-size:12px; color:#6B7280; text-transform:uppercase; letter-spacing:1px;">Tests Analyzed</p>
        </td>
        <td width="4%"></td>
        <td width="48%" style="padding:20px; background-color:{'#FFF7ED' if flagged_count > 0 else '#F0FDF4'}; border-radius:10px; text-align:center;">
          <p style="margin:0; font-size:28px; font-weight:700; color:{status_color}; font-family:'Poppins',sans-serif;">{status_text}</p>
          <p style="margin:4px 0 0; font-size:12px; color:#6B7280; text-transform:uppercase; letter-spacing:1px;">Status</p>
        </td>
      </tr>
    </table>
    
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center" style="padding:8px 0;">
          <p style="margin:0; font-size:14px; color:#6B7280;">
            Open the app to view your full report, summary, and trend charts.
          </p>
        </td>
      </tr>
    </table>"""
    
    return subject, _base_template("Report Ready", content)


def password_changed_email(name: str) -> tuple[str, str]:
    """
    Confirmation email sent after a password change.

    Returns:
        Tuple of (subject, html_body).
    """
    subject = "Password Changed — LabReport Interpreter"
    content = f"""
    <h2 style="margin:0 0 8px; font-family:'Poppins',sans-serif; font-size:20px; color:#1A1A2E;">
      Password Changed Successfully 🔒
    </h2>
    <p style="margin:0 0 24px; font-size:15px; color:#6B7280; line-height:1.6;">
      Hi {name}, your password has been updated successfully.
    </p>
    
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="padding:20px; background-color:#FEF2F2; border-radius:10px; border-left:4px solid #C0392B;">
          <strong style="color:#C0392B; font-size:14px;">⚠️ Wasn't you?</strong>
          <p style="margin:4px 0 0; font-size:13px; color:#6B7280;">
            If you didn't make this change, please secure your account immediately
            by contacting support.
          </p>
        </td>
      </tr>
    </table>"""
    
    return subject, _base_template("Password Changed", content)


def critical_values_alert_email(
    name: str,
    critical_values: list[dict],
    report_date: str,
) -> tuple[str, str]:
    """
    Urgent alert email sent when critical lab values are detected.

    Args:
        critical_values: List of dicts with test_name, value, unit, ref_low, ref_high.

    Returns:
        Tuple of (subject, html_body).
    """
    subject = "🚨 Critical Lab Values Detected — Immediate Attention Needed"

    rows_html = ""
    for cv in critical_values:
        ref_range = f"{cv.get('ref_low', '?')} - {cv.get('ref_high', '?')}"
        rows_html += f"""
        <tr>
          <td style="padding:10px 12px; border-bottom:1px solid #FEE2E2; font-size:13px; color:#1A1A2E; font-weight:600;">{cv['test_name']}</td>
          <td style="padding:10px 12px; border-bottom:1px solid #FEE2E2; font-size:13px; color:#C0392B; font-weight:700; text-align:center;">{cv['value']} {cv.get('unit', '')}</td>
          <td style="padding:10px 12px; border-bottom:1px solid #FEE2E2; font-size:13px; color:#6B7280; text-align:center;">{ref_range}</td>
        </tr>"""

    content = f"""
    <div style="padding:16px; background-color:#FEF2F2; border-radius:10px; border:2px solid #C0392B; margin-bottom:24px; text-align:center;">
      <p style="margin:0; font-size:16px; font-weight:700; color:#C0392B; font-family:'Poppins',sans-serif;">
        🚨 CRITICAL VALUES DETECTED
      </p>
    </div>
    
    <p style="margin:0 0 16px; font-size:15px; color:#6B7280; line-height:1.6;">
      Hi {name}, your lab report from <strong>{report_date}</strong> contains values that are
      significantly outside normal ranges and require immediate medical attention.
    </p>
    
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-radius:8px; overflow:hidden; border:1px solid #FEE2E2; margin-bottom:24px;">
      <tr style="background-color:#C0392B;">
        <th style="padding:10px 12px; font-size:12px; color:#FFFFFF; text-align:left; text-transform:uppercase; letter-spacing:1px;">Test</th>
        <th style="padding:10px 12px; font-size:12px; color:#FFFFFF; text-align:center; text-transform:uppercase; letter-spacing:1px;">Your Value</th>
        <th style="padding:10px 12px; font-size:12px; color:#FFFFFF; text-align:center; text-transform:uppercase; letter-spacing:1px;">Normal Range</th>
      </tr>
      {rows_html}
    </table>
    
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="padding:16px; background-color:#FFF7ED; border-radius:10px; border-left:4px solid #E29D3E;">
          <strong style="color:#E29D3E; font-size:14px;">📞 Recommendation</strong>
          <p style="margin:4px 0 0; font-size:13px; color:#6B7280;">
            Please consult your healthcare provider as soon as possible to discuss these results.
            This is an automated alert and should not replace professional medical advice.
          </p>
        </td>
      </tr>
    </table>"""
    
    return subject, _base_template("Critical Alert", content,
        "This is an automated critical alert. If these results are unexpected, please contact your healthcare provider.")


def account_deleted_email(name: str) -> tuple[str, str]:
    """
    Confirmation email sent after account deletion.

    Returns:
        Tuple of (subject, html_body).
    """
    subject = "Account Deleted — LabReport Interpreter"
    content = f"""
    <h2 style="margin:0 0 8px; font-family:'Poppins',sans-serif; font-size:20px; color:#1A1A2E;">
      Account Deleted
    </h2>
    <p style="margin:0 0 24px; font-size:15px; color:#6B7280; line-height:1.6;">
      Hi {name}, your LabReport Interpreter account and all associated data have been permanently deleted.
    </p>
    
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="padding:20px; background-color:#F0FDFA; border-radius:10px; text-align:center;">
          <p style="margin:0; font-size:14px; color:#006D77;">
            Thank you for using LabReport Interpreter. 
            You're welcome to create a new account at any time.
          </p>
        </td>
      </tr>
    </table>"""
    
    return subject, _base_template("Account Deleted", content)
