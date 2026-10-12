// Copyright (c) 2026, Guba Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Impact Assessment Report", {
    refresh(frm) {
        render_report_remark(frm);
    },
});

function stat_card(title, responded, assigned) {
    const rate = assigned ? Math.round((responded / assigned) * 100) : 0;
    const color = rate >= 75 ? "var(--green-600)" : rate >= 40 ? "var(--orange-600)" : "var(--red-600)";

    return `
        <div style="flex:1; min-width:240px; border:1px solid var(--border-color);
                    border-radius:var(--border-radius-md); padding:12px 16px; background:var(--subtle-fg);">
            <div style="font-size:12px; font-weight:600; text-transform:uppercase;
                        letter-spacing:.04em; color:var(--text-muted); margin-bottom:6px;">
                ${title}
            </div>
            <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px;">
                <div>
                    <span style="font-size:20px; font-weight:700;">${responded}</span>
                    <span style="color:var(--text-muted);">${__("of {0} responded", [assigned])}</span>
                </div>
                <span style="background:${color}; color:#fff; font-weight:600; font-size:12px;
                             padding:2px 10px; border-radius:12px;">${rate}%</span>
            </div>
            <div style="height:8px; background:var(--gray-200); border-radius:4px; overflow:hidden;">
                <div style="width:${rate}%; height:100%; background:${color};"></div>
            </div>
        </div>`;
}

function render_report_remark(frm) {
    const html = `
        <div style="display:flex; gap:12px; flex-wrap:wrap;">
            ${stat_card(__("Trainees"), cint(frm.doc.responded_count), cint(frm.doc.assigned_count))}
            ${stat_card(__("Managers"), cint(frm.doc.manager_responded_count), cint(frm.doc.manager_assigned_count))}
        </div>`;

    frm.get_field("report_remark").$wrapper.html(html);
}