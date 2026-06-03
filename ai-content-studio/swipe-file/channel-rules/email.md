# Email Channel Rules

## Subject Line
- Length: 35-50 characters
- No ALL CAPS
- Avoid spam trigger words (free, guarantee, act now)
- Personalization: {{company}} or {{role}} in subject (when relevant)
- Test: does it pass the "would I open this?" test

## Preview Text
- Always set custom preview text
- Length: 90-100 characters
- Should complement the subject line, not repeat it
- Use to add urgency or curiosity

## Body Structure
- Greeting: personalized ("Hi {{name}},")
- Opening line: reference something specific (company, role, event)
- Body: 3-5 paragraphs, max 200 words
- One idea per paragraph
- Short sentences (15-20 words average)

## Personalization Tokens
- {{name}} — first name
- {{company}} — company name
- {{role}} — their role
- {{industry}} — their industry
- {{topic}} — content topic

## CTA Rules
- One CTA per email (max)
- CTA must be unambiguous
- Button format for primary CTA
- Text link for secondary CTA
- No competing CTAs

## Links & Tracking
- UTM params: source=email&medium=email&campaign={{campaign_name}}
- At least one tracked link
- Plain text URLs for secondary links

## Signature
```
{{name}}
{{title}}, {{company}}
Book a time: [calendar link]
```

## Send Rules
- Cold outreach: Tue-Thu, 6-8am recipient timezone
- Newsletter: consistent day + time each week
- Follow-up: 3-5 business days between sends
- Max sequence: 5 touches before recycle
