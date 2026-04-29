# Verified Sources

Generated: 2026-04-28

Working rule for this folder: cite only sources that can be reopened from a stable URL, and mark anything else as unverified until manually confirmed.

## Confirmed Sources With URLs And Dates

### National Cyber Crime Reporting Portal / I4C

Confirmed victim-facing infrastructure:

- National Cyber Crime Reporting Portal: https://cybercrime.gov.in
- Cyber helpline: `1930`, confirmed in PIB/MHA releases.
- "Report and Check Suspect" and suspect repository links are present on the cybercrime.gov.in homepage/navigation.
- Learning Corner pages present on cybercrime.gov.in: Advisories, Cyber Safety Tips, Cyber Awareness, Daily Digest.

Recent I4C Daily Digest list items visible on the public list page at https://cybercrime.gov.in/Webform/daily-digest.aspx:

| Title | Date | Code | URL | Summary |
|---|---:|---|---|---|
| Daily Digest | 2026-04-28 | CD-855 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry; detail view uses ASP.NET postback and was not reliably scraped. |
| Daily Digest | 2026-04-27 | CD-854 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry; title/date/code confirmed, detail content not scraped. |
| Daily Digest | 2026-04-24 | CD-853 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry. |
| Daily Digest | 2026-04-23 | CD-852 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry. |
| Daily Digest | 2026-04-22 | CD-851 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry. |
| Daily Digest | 2026-04-21 | CD-850 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry. |
| Daily Digest | 2026-04-20 | CD-849 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry. |
| Daily Digest | 2026-04-17 | CD-848 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry. |
| Daily Digest | 2026-04-16 | CD-847 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry. |
| Daily Digest | 2026-04-15 | CD-846 | https://cybercrime.gov.in/Webform/daily-digest.aspx | I4C daily digest list entry. |

Notes: cybercrime.gov.in was reachable. The Daily Digest detail links are ASP.NET postbacks, so I did not treat detail-level claims as verified unless they appeared in a directly accessible page or another stable source.

### PIB / Ministry of Home Affairs

| Title | Date | URL | Summary |
|---|---:|---|---|
| Cyber Awareness | 2026-03-17 | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2241336 | Confirms NCRP/cybercrime.gov.in, CFCFRMS, helpline 1930, SOP issued 2026-01-02, and awareness work covering digital arrest. |
| Incidents of Cyber Crime Targeting Elderly People | 2025-07-22 | https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2146786 | Confirms I4C, NCRP, 1930, Cyber Fraud Mitigation Centre, digital-arrest awareness and caller-tune campaign. |
| Awareness Campaign on Cyber Crimes | 2024-12-10 | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2082765 | Confirms cybercrime.gov.in, 1930, I4C social channels, and digital-arrest awareness activities. |
| Digital Arrest awareness from Mann Ki Baat | 2024-10-27 | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2068698 | Confirms digital-arrest modus: impersonation of police, CBI, anti-narcotics, RBI over video call, and directs citizens to 1930/cybercrime.gov.in. |
| Mann Ki Baat transcript mentioning digital arrest | 2024-10-27 | https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2068606 | Confirms "digital arrest" is not a lawful process and recommends Stop, Think, Act plus 1930/cybercrime.gov.in. |

PIB Fact Check page status: https://pib.gov.in/factcheck.aspx was reachable, but the current fact-check cards were not exposed cleanly in static HTML. I used stable PIB press-release pages instead.

### Reserve Bank Of India / SACHET

| Title | Date | URL | Summary |
|---|---:|---|---|
| RBI cautions against frauds in the name of KYC updation | 2024-02-02 | https://www.rbi.org.in/scripts/FS_PressRelease.aspx?prid=57244 | Confirms KYC-update fraud using unsolicited calls/SMS/emails, links, false urgency, and threats of account freezing/blocking/closure. Recommends official bank confirmation and reporting on 1930/cybercrime.gov.in. |
| SACHET homepage | 2026-04-28 server date visible | https://sachet.rbi.org.in | RBI SACHET site reachable. Static homepage emphasizes investor awareness, complaints, and unauthorized deposit/scheme reporting. |
| SACHET What's New | 2026-04-28 checked | https://sachet.rbi.org.in/home/WhatsNew | List page reachable; static HTML exposed public notices/programmes but not a clean dated cyber-fraud advisory feed. |

### NPCI / BHIM / UPI

| Title | Date | URL | Summary |
|---|---:|---|---|
| UPI product overview | current page checked 2026-04-28 | https://www.npci.org.in/what-we-do/upi/product-overview/ | Confirms UPI collect request is a pull/request-money transaction where the payer approves or declines and authorizes with UPI PIN. |
| UPI FAQs | current page checked 2026-04-28 | https://www.npci.org.in/what-we-do/upi/faqs/ | Confirms UPI PIN is used to authorize bank transactions and should not be shared. |
| BHIM FAQ | current page checked 2026-04-28 | https://www.npci.org.in/what-we-do/bhim/faq/ | Confirms "Approve to Pay", collect request display, decline/block flow for unknown money requests. |
| UPI circulars page | FY 2025-26 | https://www.npci.org.in/what-we-do/upi/circular | Lists OC No. 220: discontinuing UPI Collect Request for P2P transactions. |

### CERT-In

CERT-In content is technical vulnerability/advisory material, not cyber-fraud victim-script material, but the site is reachable and recent advisories are available.

| Title | Date | URL | Summary |
|---|---:|---|---|
| CIVN-2026-0200 Quantum Networks Router vulnerabilities | 2026-04-21 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0200&pageid=PUBVLNOTES01 | Router command injection/brute-force/admin-access risks. |
| CIVN-2026-0189 PHP Composer vulnerabilities | 2026-04-16 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0189&pageid=PUBVLNOTES01 | Composer command-injection risks. |
| CIVN-2026-0188 Apache Tomcat vulnerabilities | 2026-04-16 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0188&pageid=PUBVLNOTES01 | Tomcat auth/information disclosure risks. |
| CIVN-2026-0150 Apple iOS and iPadOS vulnerabilities | 2026-03-19 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0150&pageid=PUBVLNOTES01 | Apple product critical vulnerability note. |
| CIVN-2026-0103 FileZen command injection | 2026-02-26 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0103&pageid=PUBVLNOTES01 | FileZen remote code execution risk. |
| CIVN-2026-0091 GitLab vulnerabilities | 2026-02-16 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0091&pageid=PUBVLNOTES01 | GitLab sensitive information, SSRF, XSS, DoS risks. |
| CIVN-2026-0075 OpenSSL remote code execution | 2026-02-06 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0075&pageid=PUBVLNOTES01 | OpenSSL DoS/RCE risk. |
| CIVN-2026-0053 Mozilla vulnerabilities | 2026-01-29 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0053&pageid=PUBVLNOTES01 | Firefox/Thunderbird code execution risk. |
| CIVN-2026-0025 Windows VBS Enclave privilege escalation | 2026-01-16 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0025&pageid=PUBVLNOTES01 | Windows local privilege-escalation risk. |
| CIVN-2026-0015 Trend Micro Apex Central vulnerabilities | 2026-01-13 | https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIVN-2026-0015&pageid=PUBVLNOTES01 | Critical Trend Micro Apex Central risk. |

### Reputable Public Reporting Used For Pattern Extraction

| Title | Date | URL | Summary |
|---|---:|---|---|
| FedEx scamsters strike again: Bengaluru software engineer held in digital arrest, loses Rs. 1 crore | 2024-05-22 | https://indianexpress.com/article/cities/bangalore/fedex-scam-bengaluru-software-engineer-held-digital-arrest-loses-rs-1-crore-9344267/ | Parcel/courier-to-digital-arrest pattern with narcotics allegation and impersonated investigators. |
| Bengaluru MNC product marketing head placed under digital arrest for 10 hours | 2024-09-24 | https://indianexpress.com/article/cities/bangalore/bengaluru-mnc-product-marketing-head-digital-arrest-loses-rs-51-lakh-cybercriminals-9585330/ | FedEx/Mumbai Police digital-arrest variant. |
| Karnataka HC stays criminal case against digital-arrest victim | 2026-02-04 | https://indianexpress.com/article/cities/bangalore/rs-50-lakh-loan-karnataka-hc-stays-case-against-digital-arrest-victim-10512800/lite/ | Court-linked report of loan coerced during digital arrest. |
| Digital arrest: FedEx fraudsters dupe techie of Rs. 1 crore | 2024-05-22 | https://timesofindia.indiatimes.com/city/bengaluru/fedex-fraudsters-dupe-techie-of-1cr/articleshow/110315472.cms | Fake parcel containing MDMA/passports, customs/police impersonation. |
| NPCI shutting down UPI Collect Request for P2P transactions | 2025-08-15 | https://timesofindia.indiatimes.com/technology/tech-news/npci-is-shutting-down-these-qr-code-based-upi-transactions-starting-october-1/amp_articleshow/123279266.cms | Explains misuse of collect/pull payments by fraudsters. |
| The real danger of KYC scams | 2025-05-02 | https://indianexpress.com/article/technology/tech-news-technology/you-are-one-click-away-from-losing-everything-the-real-danger-of-kyc-scams-9723005/lite/ | KYC scams with fake links, OTP fraud, and reporting to 1930/NCRP. |
| One link, total control: screen-sharing scams | 2026-02-07 | https://indianexpress.com/article/technology/tech-news-technology/one-link-total-control-how-screen-sharing-scams-are-looting-indians-10517253/ | Remote-access/screen-sharing scams under KYC, refund, and support pretexts. |

## Search Strings Checked

- `digital arrest`: confirmed in PIB/MHA, SBI, ICICI, Indian Express, Times of India.
- `1930`: confirmed in PIB/MHA, RBI KYC release, SBI cyber security page.
- `courier`, `FedEx`, `parcel`: confirmed through reputable press and bank-awareness material; not all variants have official I4C detail pages.
- `KYC`: confirmed in RBI, SBI, HDFC, ICICI, Axis, and news sources.
- `UPI collect request`: confirmed in NPCI/BHIM material and current reporting on P2P collect discontinuation.
- `Sahyog`: existence confirmed through legal/news/parliamentary-context sources, but not as the public victim-reporting endpoint. For this dataset, use `1930` and `cybercrime.gov.in` as the verified citizen-facing endpoints.
- `Trust Wallet`: no official I4C/MHA/cybercrime.gov.in/PIB/CERT-In source found for an April 27, 2026 Trust Wallet advisory.

## Claims I Could Not Verify

- "Trust Wallet Crypto Drainer advisory released yesterday, April 27, 2026": not verified from cybercrime.gov.in, MHA/PIB, CERT-In, or RBI. I found an unofficial-looking site called "Ministry of Cyber Affairs India" repeating a similar claim, but it is not a Government of India domain and should not be cited as an official advisory.
- "Sahyog Portal" as the current public cyber-fraud reporting portal: not supported. It appears in legal/news discussion as an I4C/MHA content-takedown or intermediary-coordination platform. For victim reporting, cite `1930` and `cybercrime.gov.in`.
- "MD parcel script advisory in April 2026": the narcotics/MDMA parcel variant is well documented in 2024-2025 reporting, but I did not verify a specific April 2026 official advisory for that wording.
- Nashik-specific advice: not verified from the local context and should not be included unless the submitter confirms location or local police sources.
