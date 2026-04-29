# Pilot V2 Diff

Generated: 2026-04-28

Only the 3 reviewed rows were changed. `row_id` values are preserved. No new rows were generated. No Adaption job was run.

| row_id | field | before | after |
|---|---|---|---|
| CYB-PILOT-004 | message_text | Blue Dart: तुमची shipment आज deliver होईल. Track ID BD482916. अनोळखी नंबरवरील links किंवा माहिती शेअर करू नका. -Blue Dart | Blue Dart: तुमची shipment आज deliver होईल. Track ID BD482916. अनोळखी नंबरवरून आलेल्या links उघडू नका, माहिती शेअर करू नका. -Blue Dart |
| CYB-PILOT-004 | validation_status | needs_human_review | corrected_after_review |
| CYB-PILOT-005 | message_text | कॉलरने Blue Dart delivery agent असल्याचे सांगितले. address verify नाही म्हणून SMS मधला special code dial करायला सांगितला आणि parcel आजच hold होईल अशी घाई केली. | कॉलरने Blue Dart delivery agent असल्याचे सांगितले. address confirm होत नसल्यामुळे SMS मधला special code dial करायला सांगितला आणि parcel आजच hold होईल अशी घाई केली. |
| CYB-PILOT-005 | validation_status | needs_human_review | corrected_after_review |
| CYB-PILOT-011 | message_text | Rs.125 refund ke liye UPI collect approve karo. PIN dalte hi debit reversal complete hoga. Req from MAHABANK-REFUND. | Rs.125 refund ke liye UPI collect approve karo. Debit reversal process complete hoga. Req from MAHABANK-REFUND. |
| CYB-PILOT-011 | red_flags | refund_lure\|asks_upi_pin\|unknown_collect_request\|bank_impersonation | refund_lure\|hidden_upi_pin_risk\|unknown_collect_request\|bank_impersonation |
| CYB-PILOT-011 | validation_status | needs_human_review | corrected_after_review |

## Notes

- Marathi row `CYB-PILOT-004` now uses conversational `नंबरवरून आलेल्या links` instead of literary `नंबरवरील links`.
- Marathi row `CYB-PILOT-005` now avoids the Hindi-calque `address verify नाही म्हणून`.
- Hinglish UPI scam row `CYB-PILOT-011` no longer states the PIN mechanism explicitly in the user-facing text. The hidden risk remains documented in `red_flags`.
