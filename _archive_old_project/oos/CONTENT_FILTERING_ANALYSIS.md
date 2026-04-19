# Email Content Filtering Analysis

## 📊 Current Sample Analysis (100 emails)
- **Spam/chain letters**: 3 (thespark.com, personality tests)
- **Art history papers**: 3 (your academic writing - GOOD!)
- **Personal emails**: 66 (the good stuff!)

## 🔍 Filtering Strategy

### **Keep These (High Quality Content):**
1. **Personal emails** - Your actual communication
2. **Academic writing** - Your art history papers, essays, assignments
3. **Work-related emails** - Job applications, research assistant inquiries
4. **Social coordination** - Meeting friends, making plans
5. **Technical discussions** - Problem-solving, questions

### **Remove These (Low Quality/Noise):**
1. **Spam/chain letters** - Personality tests, forwarded chains
2. **Pure forwards** - Messages with only ">From: " quoted text
3. **Auto-generated** - System messages, notifications
4. **Very short messages** - Under 50 words (likely quick replies)
5. **Commercial spam** - Marketing, unwanted emails

## 🛠️ Improved Filtering Approach

### **1. Content Quality Filters**
```python
def is_high_quality_email(content, subject):
    content = content.lower()

    # REMOVE: Spam indicators
    spam_keywords = ['thespark.com', 'personality test', 'chain letter',
                    'how well do you know me', 'forwarded message']
    if any(spam in content for spam in spam_keywords):
        return False

    # REMOVE: Pure forwards (mostly quoted text)
    quoted_ratio = content.count('>') / len(content) if content else 0
    if quoted_ratio > 0.5:  # More than 50% quoted
        return False

    # KEEP: Academic content
    academic_keywords = ['art history', 'paper', 'essay', 'assignment',
                       'professor', 'class', 'course']
    if any(academic in content for academic in academic_keywords):
        return True

    # KEEP: Personal communication
    personal_indicators = ['uchicago.edu', 'hotmail.com', 'zoheri',
                          'meeting', 'dinner', 'plans', 'can you']
    if any(personal in content for personal in personal_indicators):
        return True

    # FILTER: Length requirements
    word_count = len(content.split())
    return 50 <= word_count <= 1000  # Reasonable length
```

### **2. Topic-Aware Sampling**
Instead of random sampling, we should:
- **Cluster by topic** after cleaning
- **Sample from each cluster** to get diverse content
- **Weight by quality** - prefer high-quality personal emails

### **3. Enhanced Topic Clustering**
With cleaner data, we can:
- Use HDBSCAN (finds natural clusters)
- Better silhouette scores
- More meaningful topic extraction

## 🎯 Next Steps
1. Implement improved content filtering
2. Re-run clustering on cleaned data
3. Extract better topic distributions
4. Generate enhanced voice profiles

This should give us much better clustering results and more accurate voice profiles.

*Analysis completed: 2025-09-27*
