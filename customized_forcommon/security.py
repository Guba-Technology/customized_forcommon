import frappe
import magic
import subprocess
import tempfile
import os
from frappe.utils.file_manager import save_file
from frappe import _

# Allowed/blocked types
ALLOWED_EXTENSIONS = [".jpg", ".png", ".pdf"]
ALLOWED_MIME = ["image/jpeg", "image/png", "application/pdf"]
BLOCKED_EXTENSIONS = [".php", ".jsp", ".asp", ".exe", ".sh", ".py", ".js"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file_content(file_name: str, file_content: bytes):
    """
    Shared file validation function for secure_upload endpoint and File hook.
    Raises frappe.ValidationError if invalid.
    """
    fname = file_name.lower()

    # Extension checks
    if not any(fname.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        frappe.throw(_("File type not allowed"))
    if any(fname.endswith(ext) for ext in BLOCKED_EXTENSIONS):
        frappe.throw(_("Blocked file type"))

    # Size check
    if len(file_content) > MAX_FILE_SIZE:
        frappe.throw(_("File too large"))

    # MIME type check
    mime = magic.from_buffer(file_content[:2048], mime=True)
    if mime not in ALLOWED_MIME:
        frappe.throw(_("Invalid file content type"))

    # Optional antivirus scan
    # with tempfile.NamedTemporaryFile(delete=False) as tmp:
    #     tmp.write(file_content)
    #     tmp_path = tmp.name
    # result = subprocess.run(["clamscan", tmp_path], capture_output=True)
    # output = result.stdout.decode()
    # os.remove(tmp_path)
    # if "Infected" in output:
    #     frappe.throw(_("Malicious file detected"))


@frappe.whitelist(allow_guest=True)
def secure_upload():
    """API endpoint for browser/UI uploads"""
    file = frappe.request.files.get("file")
    if not file:
        frappe.throw(_("No file uploaded"))

    file_content = file.read()
    validate_file_content(file.filename, file_content)

    # Save the file (File document auto-created)
    file_doc = save_file(
        fname=file.filename,
        content=file_content,
        dt=None,
        dn=None,
        is_private=1
    )
    return file_doc


# ---------------------------
# File DocType hook
# ---------------------------
def validate_file_hook(doc, method):
    """
    Runs on every File document insert/update
    doc: File document
    """
    # Determine path to the file content
    file_path = (
        frappe.get_site_path("private", "files", doc.file_name)
        if doc.is_private else
        frappe.get_site_path("public", "files", doc.file_name)
    )

    # Read the content
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            content = f.read()
        validate_file_content(doc.file_name, content)
    else:
        frappe.throw(_("File content not found for validation"))