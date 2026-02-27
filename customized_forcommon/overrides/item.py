# import frappe
# import qrcode
# import barcode
# from io import BytesIO
# from frappe.utils.file_manager import save_file, remove_all
# from barcode.writer import ImageWriter

# @frappe.whitelist()
# def generate_qr_code(name):
#     item = frappe.get_doc("Item", name)
#     shelf = item.custom_shelf_number or "N/A"
#     data = f"Item Name:{item.name}\nItem Code:{item.item_code}\nItem Group:{item.item_group}\nShelf:{item.custom_shelf_number}\nRoom Number:{item.custom_room_number}\nDescription:{item.description}"
#     remove_all("Item", name)
#     qr = qrcode.QRCode(version=1, box_size=10, border=5)
#     qr.add_data(data)
#     qr.make(fit=True)
#     qr_img = qr.make_image(fill_color="black", back_color="white")
    
#     qr_buffer = BytesIO()
#     qr_img.save(qr_buffer, format="PNG")
    
#     qr_file = save_file(
#         f"{item.name}_qr.png",
#         qr_buffer.getvalue(),
#         "Item",
#         item.name,
#         is_private=0
#     )

#     # # 2. Generate Barcode (Code128)
#     # CODE128 = barcode.get_barcode_class('code128')
#     # barcode_obj = CODE128(data, writer=ImageWriter())
    
#     # barcode_buffer = BytesIO()
#     # barcode_obj.write(barcode_buffer)
    
#     # barcode_file = save_file(
#     #     f"{item.name}_barcode.png",
#     #     barcode_buffer.getvalue(),
#     #     "Item",
#     #     item.name,
#     #     is_private=0
#     # )

#     # # Update database directly to avoid recursion
#     item.custom_qr_code = qr_file.file_url

#     return qr_file.file_url