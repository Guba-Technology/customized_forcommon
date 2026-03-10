const OriginalUploader = frappe.ui.FileUploader;

frappe.ui.FileUploader = class CustomFileUploader extends OriginalUploader {
	constructor(opts = {}) {

		// hide unwanted upload options
		opts.disable_file_browser = true; // hide Library
		opts.allow_web_link = false;      // hide Link
		opts.allow_take_photo = false;    // hide Camera
		opts.allow_google_drive = false;  // hide Google Drive

		// ensure restrictions object exists
		opts.restrictions = opts.restrictions || {};

		// restrict file types
		opts.restrictions.allowed_file_types = [".pdf", ".jpg", ".png"];

		// restrict file size (5MB)
		opts.restrictions.max_file_size = 5 * 1024 * 1024;


		super(opts);
		
	}
};