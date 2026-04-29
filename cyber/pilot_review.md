# Pilot Review

Generated: 2026-04-28

Status: 12-row pilot generated and stopped for human review. No Adaption job has been run.

## Triplet TRIP-DA-HI-001

- Scam type: `digital_arrest`
- Language: Hindi
- Genuine anchor: `ANC-CYBER-002`
- Main scam pattern: `PAT-DA-004`

| row_id | variant_type | pattern_id | message_text |
|---|---|---|---|
| CYB-PILOT-001 | genuine | PAT-DA-006 | CyberDost: कोई सरकारी एजेंसी phone/video call पर गिरफ्तारी या पूछताछ नहीं करती. ऐसे call पर तुरंत 1930 पर report करें. |
| CYB-PILOT-002 | scam | PAT-DA-004 | कॉलर ने खुद को Mumbai Crime Branch बताया, कहा Aadhaar से parcel case जुड़ा है. उसने WhatsApp video call चालू रखने, परिवार को न बताने और verification amount तैयार रखने को कहा. |
| CYB-PILOT-003 | help_seeking | PAT-DA-004 | भैया, कोई CBI वाला बोल रहा है कि मैं digital arrest में हूं और video call काटना मना है. क्या सच में ऐसा होता है या 1930 पर call करूं? |

## Triplet TRIP-FC-MR-001

- Scam type: `fake_courier_parcel`
- Language: Marathi
- Genuine anchor: `ANC-SMS-030`
- Main scam pattern: `PAT-FC-008`

| row_id | variant_type | pattern_id | message_text |
|---|---|---|---|
| CYB-PILOT-004 | genuine | PAT-FC-008 | Blue Dart: तुमची shipment आज deliver होईल. Track ID BD482916. अनोळखी नंबरवरील links किंवा माहिती शेअर करू नका. -Blue Dart |
| CYB-PILOT-005 | scam | PAT-FC-008 | कॉलरने Blue Dart delivery agent असल्याचे सांगितले. address verify नाही म्हणून SMS मधला special code dial करायला सांगितला आणि parcel आजच hold होईल अशी घाई केली. |
| CYB-PILOT-006 | help_seeking | PAT-FC-008 | आई, Blue Dart वाला म्हणतो address verify नाही म्हणून एक code dial कर म्हणतोय. parcel hold होईल म्हणाला. हे खरं आहे का की 1930 ला call करू? |

## Triplet TRIP-KYC-EN-001

- Scam type: `fake_kyc`
- Language: English
- Genuine anchor: `ANC-SMS-017`
- Main scam pattern: `PAT-KYC-001`

| row_id | variant_type | pattern_id | message_text |
|---|---|---|---|
| CYB-PILOT-007 | genuine | PAT-KYC-001 | BOI-Your A/C No XXXX4187 is inactive since 15-02-2026,Please contact Branch with Fresh KYC Document for verification. |
| CYB-PILOT-008 | scam | PAT-KYC-001 | BOI KYC expired! Ur A/c will block today. Update PAN/KYC at kyc-boi-secure[.]xyz Ref:KYC482 -BOI |
| CYB-PILOT-009 | help_seeking | PAT-KYC-001 | Dad, I got SMS saying BOI KYC expired and link kyc-boi-secure[.]xyz. It says account blocks today. Should I ignore and visit branch? |

## Triplet TRIP-UPI-HIN-001

- Scam type: `upi_collect_request`
- Language: Hinglish
- Genuine anchor: `ANC-SMS-001`
- Main scam pattern: `PAT-UPI-007`

| row_id | variant_type | pattern_id | message_text |
|---|---|---|---|
| CYB-PILOT-010 | genuine | PAT-UPI-007 | A/c X4821 se Rs.125.00 UPI payment KIRAN SNACKS ko debit hua on 12-May-26. RRN: 731482905164. Not you? call bank. -MAHABANK |
| CYB-PILOT-011 | scam | PAT-UPI-007 | Rs.125 refund ke liye UPI collect approve karo. PIN dalte hi debit reversal complete hoga. Req from MAHABANK-REFUND. |
| CYB-PILOT-012 | help_seeking | PAT-UPI-007 | Bhai UPI app me MAHABANK-REFUND se collect req aaya, bol raha Rs.125 reversal ke liye PIN dalu. Receive money me PIN lagta kya? |

## Review Questions

- Does the genuine row read like a real SMS/notice for that language and surface?
- Does the scam row sound like a plausible Indian scam without becoming operationally reusable?
- Does the help-seeking row sound like a real anxious person, not a narrated summary?
- Are Hindi/Marathi inflections and code-mixing natural enough to scale?
