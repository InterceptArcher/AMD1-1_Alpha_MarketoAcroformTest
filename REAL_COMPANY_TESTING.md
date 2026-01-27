# Testing With Real Companies

## 🏢 What Works for ANY Company vs What's Limited

### ✅ WORKS FOR ALL COMPANIES (Real Logic)

These features work for **ANY email domain**:

#### 1. Email Validation
```
✅ john@anyrandomcompany.com      → Valid
✅ security@startup123.io          → Valid
✅ ops@mycompany.co.uk             → Valid
❌ notanemail                      → Invalid
❌ missing@domain                  → Invalid
```

#### 2. Domain Extraction
```
Input:  security@randomstartup.com
Output: "randomstartup.com"

Input:  john.doe@big-enterprise.co.uk
Output: "big-enterprise.co.uk"
```
**Works for ANY domain!**

#### 3. Persona Detection
```
ops@anything.com         → "Operations"
security@anything.com    → "Security"
finance@anything.com     → "Finance"
it@anything.com          → "IT"
cto@anything.com         → "IT"
cfo@anything.com         → "Finance"
ciso@anything.com        → "Security"
john@anything.com        → "Business Leader" (default)
```
**Works for ANY email prefix!**

#### 4. Buyer Stage Inference
```
?cta=compare   → "Evaluation"
?cta=learn     → "Awareness"
?cta=demo      → "Decision"
?cta=anything  → "Evaluation" (default)
```
**Works for ANY CTA parameter!**

---

### ⚠️ LIMITED: Company Enrichment (Only 6 Companies)

This is **hardcoded** for alpha - only recognizes these domains:

```javascript
✅ google.com      → "Google, Technology, Enterprise"
✅ microsoft.com   → "Microsoft, Technology, Enterprise"
✅ amazon.com      → "Amazon, E-commerce, Enterprise"
✅ apple.com       → "Apple, Technology, Enterprise"
✅ salesforce.com  → "Salesforce, Software, Enterprise"
✅ example.com     → "Example Corp, General, Mid-market"

❓ ANY OTHER      → "Unknown, General, Mid-market"
```

#### Example:
```
Input:  security@stripe.com
Result:
  ✅ Domain: "stripe.com" (works)
  ✅ Persona: "Security" (works)
  ✅ Stage: "Evaluation" (works)
  ❌ Company: "Unknown" (not in database)
  ❌ Industry: "General" (default)
  ❌ Size: "Mid-market" (default)
```

---

## 🧪 Test With Real Companies

### Test These Known Companies (Full Data):
```bash
# Google
security@google.com + ?cta=compare
→ Security, Evaluation, Google, Technology, Enterprise ✅

# Microsoft
ops@microsoft.com + ?cta=demo
→ Operations, Decision, Microsoft, Technology, Enterprise ✅

# Amazon
finance@amazon.com + ?cta=learn
→ Finance, Awareness, Amazon, E-commerce, Enterprise ✅

# Salesforce
john@salesforce.com + ?cta=compare
→ Business Leader, Evaluation, Salesforce, Software, Enterprise ✅
```

### Test Unknown Companies (Default Data):
```bash
# Stripe (not in database)
security@stripe.com + ?cta=compare
→ Security, Evaluation, Unknown, General, Mid-market ⚠️

# Shopify (not in database)
ops@shopify.com + ?cta=demo
→ Operations, Decision, Unknown, General, Mid-market ⚠️

# Your Company (not in database)
it@mycompany.io + ?cta=learn
→ IT, Awareness, Unknown, General, Mid-market ⚠️
```

---

## 🔧 How to Add More Companies

Right now, you need to manually edit the code. Open:
```
lib/utils/enrichment.ts
```

Add entries to `companyDatabase`:
```typescript
const companyDatabase: Record<string, CompanyData> = {
  // ... existing entries ...

  'stripe.com': {
    company_name: 'Stripe',
    industry: 'Fintech',
    company_size: 'Enterprise',
  },
  'shopify.com': {
    company_name: 'Shopify',
    industry: 'E-commerce',
    company_size: 'Enterprise',
  },
  'acme-corp.com': {
    company_name: 'Acme Corporation',
    industry: 'Manufacturing',
    company_size: 'Mid-market',
  },
};
```

Then restart the server.

---

## 🚀 Production Solution: Real Company Enrichment APIs

In production, you'd replace the hardcoded lookup with a **real enrichment API**:

### Option 1: Clearbit (Recommended)
- **API**: https://clearbit.com/enrichment
- **Cost**: $99/month for 2,500 lookups
- **Data**: Company name, industry, size, logo, social, revenue
- **Coverage**: 20+ million companies

Example integration:
```typescript
async function enrichCompanyData(domain: string) {
  const response = await fetch(
    `https://company.clearbit.com/v2/companies/find?domain=${domain}`,
    { headers: { Authorization: `Bearer ${process.env.CLEARBIT_API_KEY}` } }
  );

  const data = await response.json();
  return {
    company_name: data.name,
    industry: data.category.industry,
    company_size: data.metrics.employees > 1000 ? 'Enterprise' : 'Mid-market',
  };
}
```

### Option 2: ZoomInfo
- **API**: https://www.zoominfo.com/
- **Cost**: Custom pricing (expensive)
- **Data**: Very detailed B2B data
- **Coverage**: 100+ million companies

### Option 3: Hunter.io
- **API**: https://hunter.io/domain-search
- **Cost**: $49/month for 1,000 lookups
- **Data**: Basic company info
- **Coverage**: Smaller database but affordable

---

## 📊 What Real Claude AI Will Do

Even with "Unknown" company data, Claude AI will still generate good content because:

1. **Persona is detected** correctly (Security, Operations, etc.)
2. **Buyer stage is inferred** correctly (Evaluation, Decision, etc.)
3. **Claude is smart** - it can work with partial data

Example with unknown company:
```
Input:
  Email: security@randomstartup.io
  CTA: compare
  Company: "Unknown"
  Industry: "General"

Claude Output (with real AI):
  Headline: "Enterprise-Grade Security for Growing Companies"
  Subheadline: "Protect your business with security solutions
                designed for teams evaluating their options"
  Value Props:
    1. "Zero-Trust Architecture" (tailored to Security persona)
    2. "Compliance Automation" (Security role focus)
    3. "Rapid Deployment" (good for any company)
```

Claude is **creative and adaptive** - it doesn't need perfect data.

---

## 🎯 Bottom Line

### What Works for ALL Companies:
✅ Email validation
✅ Domain extraction
✅ Persona detection (ops@, security@, etc.)
✅ Buyer stage inference (from CTA)
✅ Full UI/UX workflow
✅ Claude AI content generation (when enabled)

### What's Limited in Alpha:
⚠️ Company name recognition (only 6 companies)
⚠️ Industry detection (defaults to "General")
⚠️ Company size detection (defaults to "Mid-market")

### For Production:
🚀 Add Clearbit or similar API ($99/mo)
🚀 Get real company data for 20M+ companies
🚀 Zero code changes needed (just swap the function)

### For Your Demo:
✅ Use one of the 6 known companies (Google, Microsoft, etc.)
✅ Or explain: "For unknown companies, we default to General industry"
✅ With real AI, it still works great even with Unknown company

---

## 🧪 Quick Test Script

Test all scenarios at once:
```bash
# Test known companies
curl -X POST http://localhost:3000/api/personalize \
  -H "Content-Type: application/json" \
  -d '{"email":"security@google.com","cta":"compare"}'

curl -X POST http://localhost:3000/api/personalize \
  -H "Content-Type: application/json" \
  -d '{"email":"ops@microsoft.com","cta":"demo"}'

# Test unknown company
curl -X POST http://localhost:3000/api/personalize \
  -H "Content-Type: application/json" \
  -d '{"email":"security@unknownstartup.io","cta":"compare"}'
```

Look for:
- `"company": "Google"` vs `"company": "Unknown"`
- Persona is always correct
- Buyer stage is always correct

---

## 💡 Recommendation

For your presentation:
1. **Demo with known companies** (Google, Microsoft) - shows full capability
2. **Mention**: "Company enrichment uses Clearbit in production ($99/mo)"
3. **Explain**: "Even unknown companies get personalized content based on role and intent"

The persona detection and buyer stage inference work for **ANY company** - that's the real value!
