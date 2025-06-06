# K-Pop Sentiment Analyzer - User Guide

## 📋 Table of Contents
1. [Managing Sentiment Labels](#managing-sentiment-labels)
2. [Understanding the Analysis Engine](#understanding-the-analysis-engine)
3. [Customizing Analysis Settings](#customizing-analysis-settings)
4. [GUI Label Management](#gui-label-management)
5. [Non-Technical User Guide](#non-technical-user-guide)

---

## 🏷️ Managing Sentiment Labels

### What Are Sentiment Labels?

Sentiment labels are categories that help classify the emotional tone and intent of K-Pop related text. Think of them as "emotional buckets" where different types of fan comments, posts, and discussions are sorted.

### Current 10 K-Pop Sentiment Labels

1. **ENTHUSIASTIC_SUPPORT** (Low Risk) - Super positive fan reactions
2. **NOSTALGIC_APPRECIATION** (Low Risk) - Missing past eras or memories
3. **ANTICIPATORY_EXCITEMENT** (Low Risk) - Excitement about upcoming releases
4. **PROTECTIVE_DEFENSIVE** (Medium Risk) - Defending idols from criticism
5. **CRITICAL_DISAPPOINTMENT** (Medium Risk) - Constructive fan criticism
6. **NEUTRAL_FACTUAL** (Low Risk) - Objective information sharing
7. **COMPETITIVE_RIVALRY** (High Risk) - Fan wars and comparisons
8. **SARCASTIC_MOCKERY** (High Risk) - Sarcasm and passive-aggressive comments
9. **MALICIOUS_COORDINATED** (Very High Risk) - Organized attacks or hate campaigns
10. **MIXED_CONFLICTED** (Medium Risk) - Complex emotions with mixed feelings

### How to Create New Sentiment Labels

#### Step 1: Define Your Label
Before creating a new label, ask yourself:
- **What emotion or intent does this represent?**
- **Is it different enough from existing labels?**
- **What risk level should it have?**
- **What keywords would indicate this sentiment?**

#### Step 2: Add to the Code
Edit the `sentiment_labels.py` file:

```python
# Add your new label to the SENTIMENT_LABELS dictionary
SENTIMENT_LABELS = {
    # ... existing labels ...
    11: {
        'name': 'YOUR_NEW_LABEL_NAME',
        'description': 'Clear description of what this label represents',
        'risk_level': 'Low',  # Low, Medium, High, Very High
        'keywords': ['keyword1', 'keyword2', 'keyword3'],
        'patterns': ['specific phrases', 'emotional indicators'],
        'examples': [
            'Example text that would match this label',
            'Another example showing this sentiment'
        ]
    }
}
```

#### Step 3: Update the Analysis Engine
In `sentiment_analyzer.py`, add classification logic:

```python
def classify_your_new_label(self, text, preprocessed_text):
    """
    Detect YOUR_NEW_LABEL_NAME sentiment
    
    Args:
        text (str): Original text
        preprocessed_text (str): Cleaned text
        
    Returns:
        float: Confidence score (0-1)
    """
    confidence = 0.0
    text_lower = preprocessed_text.lower()
    
    # Check for specific keywords
    keyword_matches = sum(1 for keyword in ['your', 'keywords'] if keyword in text_lower)
    if keyword_matches > 0:
        confidence += 0.3 * (keyword_matches / len(['your', 'keywords']))
    
    # Check for specific patterns
    if 'specific pattern' in text_lower:
        confidence += 0.4
    
    # Add more detection logic here
    
    return min(confidence, 1.0)
```

#### Step 4: Test Your New Label
Create test cases to ensure your label works correctly:

```python
# Test examples
test_texts = [
    "Text that should match your new label",
    "Text that should NOT match your new label"
]

for text in test_texts:
    result = analyzer.analyze_sentiment(text)
    print(f"Text: {text}")
    print(f"Predicted: {result['label_name']}")
    print(f"Confidence: {result['confidence']:.2%}")
```

### How to Edit Existing Labels

#### Modifying Keywords
To improve detection accuracy, you can add or remove keywords:

```python
# In sentiment_labels.py
SENTIMENT_LABELS[1]['keywords'].extend(['new_keyword1', 'new_keyword2'])

# Or replace entirely
SENTIMENT_LABELS[1]['keywords'] = ['updated', 'keyword', 'list']
```

#### Adjusting Risk Levels
Change risk levels based on your community's needs:

```python
# Make a label more/less risky
SENTIMENT_LABELS[7]['risk_level'] = 'Medium'  # Changed from High
```

#### Updating Descriptions
Keep descriptions clear and helpful:

```python
SENTIMENT_LABELS[1]['description'] = 'Updated, clearer description of this sentiment'
```

### How to Delete Labels

#### Step 1: Remove from Labels Dictionary
```python
# In sentiment_labels.py
# Simply remove or comment out the label
# del SENTIMENT_LABELS[11]  # Removes label 11
```

#### Step 2: Update Database
If you have existing data, you may need to handle it:

```python
# Option 1: Reassign to another label
UPDATE sentiment_analysis SET predicted_label = 10 WHERE predicted_label = 11;

# Option 2: Delete all data with this label
DELETE FROM sentiment_analysis WHERE predicted_label = 11;
```

#### Step 3: Update Analysis Logic
Remove any specific classification methods for the deleted label.

---

## 🔍 Understanding the Analysis Engine

### How Sentiment Analysis Works (Simple Explanation)

Think of the sentiment analyzer as a very smart reading assistant that:

1. **Reads the text** you give it
2. **Cleans it up** by removing URLs, extra spaces, etc.
3. **Looks for clues** like specific words, phrases, and patterns
4. **Compares** what it finds to what it knows about each sentiment type
5. **Makes a decision** about which sentiment fits best
6. **Gives a confidence score** showing how sure it is

### The Analysis Process Step-by-Step

#### Step 1: Text Preprocessing
```
Original: "OMG @BTS_official SLAYED this performance!!! 🔥🔥 https://youtube.com/watch"
Cleaned:  "OMG BTS SLAYED this performance"
```

**What happens:**
- URLs are removed
- @mentions are cleaned (but preserved)
- Extra punctuation is normalized
- Emojis are handled appropriately

#### Step 2: Keyword Detection
The system looks for specific words that indicate different sentiments:

**Enthusiastic Support Keywords:**
- love, amazing, perfect, queen, king, talent, slay, iconic

**Sarcastic Mockery Keywords:**
- sure, right, okay, imagine (in certain contexts)

**Competitive Rivalry Keywords:**
- better than, outsold, flop, comparison

#### Step 3: Pattern Recognition
Beyond individual words, the system looks for patterns:

**Enthusiasm Patterns:**
- Multiple exclamation marks (!!!)
- ALL CAPS words
- Fire emojis and positive emojis
- Superlative language (best, greatest, most)

**Sarcasm Patterns:**
- Quotation marks around positive words
- Contradictory statements
- Eye-roll emojis
- Specific phrase structures

#### Step 4: Confidence Calculation
The system combines all evidence to create a confidence score:

```
Confidence = (Keyword Score × 0.4) + (Pattern Score × 0.3) + (Context Score × 0.3)
```

**Example:**
- Text: "OMG they absolutely SLAYED this performance! 🔥"
- Keywords found: "SLAYED" (enthusiastic) = 0.6
- Patterns found: ALL CAPS + exclamation + fire emoji = 0.8
- Context: Positive overall tone = 0.7
- **Final Confidence: (0.6 × 0.4) + (0.8 × 0.3) + (0.7 × 0.3) = 0.69 (69%)**

### Risk Assessment System

Each sentiment has a risk level that helps identify potentially problematic content:

- **Low Risk (Green):** Positive, constructive content that's safe
- **Medium Risk (Yellow):** Emotional content that might need monitoring
- **High Risk (Orange):** Potentially inflammatory content requiring attention
- **Very High Risk (Red):** Dangerous content needing immediate review

---

## ⚙️ Customizing Analysis Settings

### Adjusting Sensitivity

#### Making Detection More Sensitive
If the system is missing sentiment that you think it should catch:

```python
# In sentiment_analyzer.py, lower the confidence thresholds
def classify_enthusiastic_support(self, text, preprocessed_text):
    # ... existing code ...
    
    # Lower threshold for easier detection
    if confidence >= 0.3:  # Changed from 0.5
        return confidence
    return 0.0
```

#### Making Detection Less Sensitive
If the system is catching too much:

```python
# Raise the confidence threshold
if confidence >= 0.7:  # Changed from 0.5
    return confidence
return 0.0
```

### Adding Custom Keywords

#### For Your Specific Community
Add keywords that are specific to your fandom or community:

```python
# Add to sentiment_labels.py
SENTIMENT_LABELS[1]['keywords'].extend([
    'your_fandom_specific_term',
    'local_slang_word',
    'community_inside_joke'
])
```

#### For Different Languages
Add keywords in other languages:

```python
# Korean keywords
SENTIMENT_LABELS[1]['keywords'].extend([
    '사랑해',  # saranghae (love)
    '대박',    # daebak (awesome)
    '최고'     # choego (best)
])
```

### Customizing Risk Levels

#### Adjusting for Your Use Case
Different communities may have different tolerance levels:

```python
# For a more conservative approach (stricter)
SENTIMENT_LABELS[4]['risk_level'] = 'High'  # Changed from Medium

# For a more lenient approach
SENTIMENT_LABELS[7]['risk_level'] = 'Medium'  # Changed from High
```

### Fine-Tuning Detection Logic

#### Adding New Pattern Detection
```python
def detect_custom_pattern(self, text):
    """Detect your custom pattern"""
    confidence = 0.0
    
    # Example: Detect excessive emoji use
    emoji_count = len(re.findall(r'[😀-🙏]', text))
    if emoji_count > 3:
        confidence += 0.3
    
    # Example: Detect specific phrase structures
    if re.search(r'when .+ said .+', text.lower()):
        confidence += 0.4
    
    return min(confidence, 1.0)
```

---

## 🖥️ GUI Label Management

### Adding Label Management to the Web Interface

Let's add a new page for managing labels directly through the web interface:

#### Step 1: Create Label Management Route
Add to `app.py`:

```python
@app.route('/manage_labels')
def manage_labels():
    """Display label management interface"""
    from sentiment_labels import SENTIMENT_LABELS
    return render_template('manage_labels.html', labels=SENTIMENT_LABELS)

@app.route('/edit_label/<int:label_id>', methods=['GET', 'POST'])
def edit_label(label_id):
    """Edit a specific label"""
    if request.method == 'POST':
        # Handle label updates
        new_keywords = request.form.get('keywords', '').split(',')
        new_risk_level = request.form.get('risk_level')
        
        # Update the label (in a real app, save to database)
        # For now, this would need to modify the file
        
        flash(f'Label {label_id} updated successfully!', 'success')
        return redirect(url_for('manage_labels'))
    
    # GET request - show edit form
    from sentiment_labels import SENTIMENT_LABELS
    label = SENTIMENT_LABELS.get(label_id)
    return render_template('edit_label.html', label=label, label_id=label_id)
```

#### Step 2: Create Label Management Template
Create `templates/manage_labels.html`:

```html
{% extends "base.html" %}

{% block title %}Manage Labels - K-Pop Sentiment Analyzer{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <h1><i class="fas fa-tags"></i> Manage Sentiment Labels</h1>
            <p class="lead">Create, edit, and delete sentiment labels to customize your analysis.</p>
        </div>
    </div>

    <!-- Add New Label Button -->
    <div class="row mb-4">
        <div class="col-12">
            <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addLabelModal">
                <i class="fas fa-plus"></i> Add New Label
            </button>
        </div>
    </div>

    <!-- Labels List -->
    <div class="row">
        {% for label_id, label in labels.items() %}
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">{{ label.name.replace('_', ' ').title() }}</h5>
                    <span class="badge 
                        {% if label.risk_level == 'Low' %}bg-success
                        {% elif label.risk_level == 'Medium' %}bg-warning
                        {% elif label.risk_level == 'High' %}bg-danger
                        {% else %}bg-dark{% endif %}">
                        {{ label.risk_level }} Risk
                    </span>
                </div>
                <div class="card-body">
                    <p class="card-text">{{ label.description }}</p>
                    
                    <h6>Keywords:</h6>
                    <div class="mb-3">
                        {% for keyword in label.keywords[:5] %}
                        <span class="badge bg-secondary me-1">{{ keyword }}</span>
                        {% endfor %}
                        {% if label.keywords|length > 5 %}
                        <span class="text-muted">+{{ label.keywords|length - 5 }} more</span>
                        {% endif %}
                    </div>
                    
                    <h6>Example:</h6>
                    <blockquote class="blockquote-footer">
                        {{ label.examples[0] if label.examples else 'No example available' }}
                    </blockquote>
                </div>
                <div class="card-footer">
                    <a href="{{ url_for('edit_label', label_id=label_id) }}" class="btn btn-primary btn-sm">
                        <i class="fas fa-edit"></i> Edit
                    </a>
                    <button class="btn btn-danger btn-sm" onclick="deleteLabel({{ label_id }})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<!-- Add New Label Modal -->
<div class="modal fade" id="addLabelModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add New Sentiment Label</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="POST" action="{{ url_for('add_label') }}">
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="labelName" class="form-label">Label Name</label>
                        <input type="text" class="form-control" id="labelName" name="name" required>
                        <div class="form-text">Use UPPERCASE_WITH_UNDERSCORES format</div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="labelDescription" class="form-label">Description</label>
                        <textarea class="form-control" id="labelDescription" name="description" rows="3" required></textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label for="riskLevel" class="form-label">Risk Level</label>
                        <select class="form-select" id="riskLevel" name="risk_level" required>
                            <option value="Low">Low Risk</option>
                            <option value="Medium">Medium Risk</option>
                            <option value="High">High Risk</option>
                            <option value="Very High">Very High Risk</option>
                        </select>
                    </div>
                    
                    <div class="mb-3">
                        <label for="keywords" class="form-label">Keywords</label>
                        <input type="text" class="form-control" id="keywords" name="keywords" 
                               placeholder="keyword1, keyword2, keyword3">
                        <div class="form-text">Separate keywords with commas</div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="examples" class="form-label">Example Text</label>
                        <textarea class="form-control" id="examples" name="examples" rows="2" 
                                  placeholder="Example text that would match this label"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-success">Add Label</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
function deleteLabel(labelId) {
    if (confirm('Are you sure you want to delete this label? This action cannot be undone.')) {
        fetch(`/delete_label/${labelId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error deleting label: ' + data.error);
            }
        });
    }
}
</script>
{% endblock %}
```

### Desktop GUI Label Management

For the CustomTkinter desktop application, add a label management panel:

```python
def create_label_management_panel(self):
    """Create label management interface"""
    self.label_panel = ctk.CTkFrame(self.content_frame)
    
    # Title
    title = ctk.CTkLabel(
        self.label_panel,
        text="Sentiment Label Management",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title.pack(pady=20)
    
    # Controls frame
    controls_frame = ctk.CTkFrame(self.label_panel)
    controls_frame.pack(fill="x", padx=20, pady=10)
    
    # Add new label button
    add_btn = ctk.CTkButton(
        controls_frame,
        text="➕ Add New Label",
        command=self.show_add_label_dialog,
        height=40
    )
    add_btn.pack(side="left", padx=20, pady=20)
    
    # Import/Export buttons
    import_btn = ctk.CTkButton(
        controls_frame,
        text="📥 Import Labels",
        command=self.import_labels,
        height=40
    )
    import_btn.pack(side="left", padx=10, pady=20)
    
    export_btn = ctk.CTkButton(
        controls_frame,
        text="📤 Export Labels",
        command=self.export_labels,
        height=40
    )
    export_btn.pack(side="left", padx=10, pady=20)
    
    # Labels list
    self.labels_list = ctk.CTkScrollableFrame(self.label_panel)
    self.labels_list.pack(fill="both", expand=True, padx=20, pady=10)
    
    self.refresh_labels_list()

def show_add_label_dialog(self):
    """Show dialog for adding new label"""
    dialog = ctk.CTkToplevel(self.root)
    dialog.title("Add New Sentiment Label")
    dialog.geometry("600x500")
    dialog.transient(self.root)
    dialog.grab_set()
    
    # Form fields
    ctk.CTkLabel(dialog, text="Label Name:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(20, 5))
    name_entry = ctk.CTkEntry(dialog, placeholder_text="LABEL_NAME")
    name_entry.pack(fill="x", padx=20, pady=(0, 10))
    
    ctk.CTkLabel(dialog, text="Description:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
    desc_text = ctk.CTkTextbox(dialog, height=80)
    desc_text.pack(fill="x", padx=20, pady=(0, 10))
    
    ctk.CTkLabel(dialog, text="Risk Level:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
    risk_option = ctk.CTkOptionMenu(dialog, values=["Low", "Medium", "High", "Very High"])
    risk_option.pack(fill="x", padx=20, pady=(0, 10))
    
    ctk.CTkLabel(dialog, text="Keywords (comma-separated):", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(10, 5))
    keywords_entry = ctk.CTkEntry(dialog, placeholder_text="keyword1, keyword2, keyword3")
    keywords_entry.pack(fill="x", padx=20, pady=(0, 10))
    
    # Buttons
    button_frame = ctk.CTkFrame(dialog)
    button_frame.pack(fill="x", padx=20, pady=20)
    
    def save_label():
        # Validate and save the new label
        name = name_entry.get().strip().upper()
        description = desc_text.get("1.0", "end-1c").strip()
        risk_level = risk_option.get()
        keywords = [k.strip() for k in keywords_entry.get().split(",") if k.strip()]
        
        if not all([name, description, keywords]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Add to labels (this would save to file/database in real implementation)
        self.add_new_label(name, description, risk_level, keywords)
        dialog.destroy()
        self.refresh_labels_list()
    
    ctk.CTkButton(button_frame, text="Save", command=save_label).pack(side="right", padx=10)
    ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy).pack(side="right")
```

---

## 👥 Non-Technical User Guide

### Understanding Sentiment Analysis (No Tech Background Needed)

#### What Is Sentiment Analysis?
Imagine you have a friend who's really good at reading people's emotions from their text messages. They can tell when someone is:
- Genuinely excited vs. being sarcastic
- Angry vs. just disappointed
- Trying to start drama vs. sharing facts

That's essentially what sentiment analysis does - it reads text and figures out the emotional tone and intent behind it.

#### Why Is This Important for K-Pop Communities?

**For Fans:**
- Understand overall community mood about comebacks, performances, or news
- Identify when discussions are getting toxic before they escalate
- Find genuinely positive content vs. fake enthusiasm

**For Content Creators:**
- Know how your content is being received
- Identify which topics generate positive vs. negative responses
- Spot potential issues early

**For Community Managers:**
- Monitor community health
- Identify content that needs moderation
- Understand fan sentiment trends

### How to Use the System (Step-by-Step)

#### Basic Analysis
1. **Open the application** (web browser or desktop app)
2. **Go to "Analyze Text"** section
3. **Paste or type** the K-Pop related text you want to analyze
4. **Click "Analyze"** button
5. **Read the results:**
   - **Sentiment:** What emotion/intent was detected
   - **Confidence:** How sure the system is (higher = more confident)
   - **Risk Level:** How potentially problematic the content is

#### Understanding Results

**Example Analysis:**
```
Text: "OMG BTS absolutely SLAYED this performance! 🔥"
Result: ENTHUSIASTIC_SUPPORT (85% confidence, Low Risk)
```

**What this means:**
- The text shows genuine enthusiasm and support
- The system is 85% confident in this classification
- This is low-risk content (positive and safe)

#### Managing Your Data

**Viewing Analysis History:**
1. Go to "Manage Data" section
2. See all previous analyses
3. Sort by date, sentiment, or confidence

**Correcting Mistakes:**
1. Find an analysis that seems wrong
2. Click "Edit" next to it
3. Select the correct sentiment label
4. Click "Save" - this helps the system learn!

**Exporting Data:**
1. Go to "Statistics" or "Manage Data"
2. Click "Export Data"
3. Choose format (Excel, CSV, JSON)
4. Save to your computer

### Customizing for Your Community

#### Adding Community-Specific Terms

**Why do this?**
Every fandom has unique slang, inside jokes, and terminology. Teaching the system these terms makes it more accurate for your community.

**How to do it:**
1. Go to "Manage Labels" section
2. Find the relevant sentiment label
3. Click "Edit"
4. Add your community's terms to the keywords list
5. Save changes

**Examples:**
- Add your fandom name and variations
- Include common abbreviations your community uses
- Add inside jokes or memes that indicate certain emotions

#### Adjusting Sensitivity

**Too Sensitive (catching too much):**
- The system flags normal discussions as problematic
- Solution: Increase confidence thresholds in settings

**Not Sensitive Enough (missing issues):**
- The system misses obviously sarcastic or toxic content
- Solution: Decrease confidence thresholds or add more keywords

#### Setting Risk Levels for Your Community

Different communities have different tolerance levels:

**Conservative Community:**
- Set stricter risk levels
- Flag competitive language as higher risk
- Be more cautious with sarcasm detection

**Relaxed Community:**
- Allow more competitive banter
- Focus mainly on clearly malicious content
- Higher tolerance for emotional expression

### Troubleshooting Common Issues

#### "The system keeps getting my sentiment wrong"

**Possible causes:**
1. **Missing keywords:** Your community uses terms the system doesn't know
2. **Context differences:** Your community's context is different from training data
3. **Sarcasm detection:** System might miss subtle sarcasm patterns

**Solutions:**
1. Add your community's specific terms to relevant labels
2. Manually correct wrong analyses to help the system learn
3. Adjust confidence thresholds in settings

#### "Results seem inconsistent"

**Possible causes:**
1. **Ambiguous text:** Some text genuinely has mixed emotions
2. **Insufficient keywords:** Not enough indicators for confident classification
3. **Conflicting signals:** Text has both positive and negative elements

**Solutions:**
1. Look at confidence scores - low confidence indicates uncertainty
2. Use the "Mixed/Conflicted" label for genuinely ambiguous content
3. Add more specific keywords to improve detection

#### "The system is too slow"

**Possible causes:**
1. **Large text input:** Very long texts take more time to process
2. **Many analyses at once:** Batch processing can be slow
3. **Complex analysis:** Advanced features require more processing

**Solutions:**
1. Break large texts into smaller chunks
2. Process in smaller batches
3. Use basic analysis mode for faster results

### Best Practices

#### For Accurate Results
1. **Provide context:** Include enough text for the system to understand
2. **Use representative samples:** Don't just analyze extreme examples
3. **Regular updates:** Keep keywords and labels current with community evolution
4. **Manual verification:** Check and correct results to improve accuracy

#### For Community Management
1. **Monitor trends:** Look at overall patterns, not just individual posts
2. **Focus on high-risk content:** Prioritize reviewing flagged content
3. **Understand limitations:** The system is a tool, not a replacement for human judgment
4. **Regular maintenance:** Update labels and keywords as your community evolves

#### For Research and Analysis
1. **Collect sufficient data:** Analyze enough content for meaningful insights
2. **Consider time periods:** Compare different time periods (before/after events)
3. **Export regularly:** Keep backups of your analysis data
4. **Document changes:** Keep track of when you modify labels or settings

This system is designed to grow and improve with your community. The more you use it and provide feedback through corrections, the better it becomes at understanding your specific community's communication patterns and needs.