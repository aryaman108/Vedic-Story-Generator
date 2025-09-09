# 🔧 Gemini Pro API Troubleshooting Guide

## Issue: "AI Service Quota Exceeded" Even With Pro API

If you're getting quota exceeded errors despite having a Gemini Pro API subscription, follow these troubleshooting steps:

### 1. ✅ Verify Your API Key
- Check your `.env` file contains the correct API key:
```bash
GEMINI_API_KEY=AIzaSyCT0-gaHjlGkNTwp2CscXBRQpxWCSe9wfI
```
- Make sure there are no extra spaces or characters

### 2. ✅ Check Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** → **Credentials**
4. Verify your API key is listed and enabled

### 3. ✅ Enable Billing
1. In Google Cloud Console, go to **Billing**
2. Ensure billing is enabled for your project
3. Link a valid payment method

### 4. ✅ Verify Pro Subscription
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Check your subscription status
3. Ensure your Pro plan is active

### 5. ✅ Check API Quotas
1. In Google Cloud Console, go to **APIs & Services** → **Quotas**
2. Search for "Generative Language API"
3. Verify your quotas are set to Pro levels (not Free tier)

### 6. ✅ Test API Key
Run this test to verify your API key works:
```bash
cd Mythoscribe
python -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Hello')
print('API Key works!' if response else 'API Key issue')
"
```

### 7. ✅ Alternative Solutions

#### Option A: Use Different Model
If quota issues persist, you can modify the model in `vedic_story_generator.py`:
```python
# Change from:
model = genai.GenerativeModel('gemini-1.5-flash')
# To:
model = genai.GenerativeModel('gemini-1.5-pro')
```

#### Option B: Wait for Reset
Free tier quotas reset daily at midnight Pacific Time (PT).

#### Option C: Contact Support
- [Google AI Support](https://support.google.com/googleai)
- Include your project ID and API key (first 10 characters only)

### 8. ✅ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Free tier" in error message | Enable billing and upgrade to Pro |
| API key not working | Regenerate API key in Google Cloud Console |
| Quota still showing Free tier | Wait 24-48 hours after billing activation |
| "Invalid API key" | Check for typos in .env file |

### 9. ✅ Monitor Usage
- Check your API usage in Google Cloud Console
- Monitor costs to avoid unexpected charges
- Set up billing alerts

### 10. ✅ Still Having Issues?
If problems persist:
1. Create a new Google Cloud project
2. Generate a fresh API key
3. Enable billing immediately
4. Test the new setup

---

## 🎯 Quick Fix Commands

```bash
# Test API key
cd Mythoscribe && python -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
try:
    response = model.generate_content('Test')
    print('✅ API works!')
except Exception as e:
    print(f'❌ Error: {e}')
"

# Check environment
cd Mythoscribe && python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('GEMINI_API_KEY')
print(f'API Key loaded: {key[:10]}...' if key else 'No API key found')
"
```

## 📞 Need Help?
- Check the [Gemini API Documentation](https://ai.google.dev/docs)
- Visit [Google AI Studio](https://aistudio.google.com/)
- Contact [Google Cloud Support](https://cloud.google.com/support)

---

**Remember**: Pro API limits are much higher than Free tier (2,000+ requests/day vs 50 requests/day)