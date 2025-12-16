"""LLM service using Ollama - Enhanced with multi-strategy classification"""
import ollama
import logging
import re
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)


class LLMService:
    """Handles all LLM operations with optimized classification"""
    
    # Keywords for intelligent multi-strategy classification (12 categories)
    CATEGORY_KEYWORDS = {
        "BackendCode": {
            "strong": ["def ", "class ", "import ", "return", "function", "async", "await", "class ", "def ",
                      "endpoint", "route", "middleware", "database", "query", "orm", "sql", "nosql",
                      "server", "api", "rest"],
            "weak": ["backend", "server-side", "python", "java", "nodejs"]
        },
        "FrontendCode": {
            "strong": ["<div", "<button", "<html", "</html>", "<head", "<body", "<!doctype",
                      "<input", "<form", "<script", "<style", "<nav", "<header", "<footer",
                      "<meta", "<link", "<span", "<section", "<article",
                      "react", "vue", "angular", "html", "css", "javascript",
                      "dom", "component", "hook", "state", "props", "render", "jsx", "tsx",
                      "onclick", "onchange", "addeventlistener", "queryselector"],
            "weak": ["frontend", "ui", "interface", "web", "client-side", "browser"]
        },
        "Code": {
            "strong": ["def ", "class ", "import ", "function", "return", "if ", "else", "for ", "while ",
                      "try", "except", "catch", "throw", "const ", "let ", "var ",
                      "public ", "private ", "protected", "void", "int ", "string",
                      "print(", "console.log", "cout", "system.out"],
            "weak": ["code", "script", "program", "algorithm", "logic"]
        },
        "DataScience": {
            "strong": ["numpy", "pandas", "matplotlib", "sklearn", "tensorflow", "pytorch", "model",
                      "dataset", "training", "neural", "gradient", "epoch", "accuracy", "loss",
                      "feature", "prediction", "regression", "classification"],
            "weak": ["data", "analysis", "ml", "machine learning", "ai"]
        },
        "Documentation": {
            "strong": ["## ", "# ", "api", "endpoint", "rest", "http", "json", "schema", "response",
                      "parameter", "authentication", "authorization", "oauth", "guide", "tutorial",
                      "usage", "example", "reference", "specification"],
            "weak": ["help", "explain", "describe", "design", "architecture", "pattern"]
        },
        "Education": {
            "strong": ["question", "answer", "quiz", "exercise", "test", "exam", "learning", "course",
                      "lesson", "assignment", "homework", "solution", "evaluate", "understand",
                      "concept", "theory", "principle", "chapter", "unit ", "module",
                      "lecture", "tutorial", "semester", "grade"],
            "weak": ["teaching", "study", "student", "educational", "learn"]
        },
        "Healthcare": {
            "strong": ["medical", "patient", "diagnosis", "treatment", "disease", "clinical",
                      "healthcare", "hospital", "physician", "symptoms", "medication", "therapy",
                      "dicom", "hl7", "nifti"],
            "weak": ["health", "medicine", "doctor", "care"]
        },
        "Legal": {
            "strong": ["contract", "agreement", "clause", "liability", "copyright", "patent",
                      "terms", "conditions", "legal", "law", "regulation", "compliance",
                      "court", "lawsuit", "attorney", "jurisdiction"],
            "weak": ["legal", "lawyer", "law", "rights"]
        },
        "Finance": {
            "strong": ["revenue", "profit", "cost", "budget", "investment", "roi", "financial",
                      "balance sheet", "cash flow", "fiscal", "accounting", "audit",
                      "stock", "dividend", "equity"],
            "weak": ["money", "business", "financial", "payment"]
        },
        "Business": {
            "strong": ["strategy", "marketing", "sales", "customer", "market", "growth",
                      "operations", "management", "leadership", "organization", "team",
                      "planning", "objective"],
            "weak": ["company", "work", "plan", "goal"]
        },
        "ResearchPaper": {
            "strong": ["abstract", "introduction", "methodology", "results", "conclusion",
                      "research", "study", "analysis", "hypothesis", "experiment",
                      "latex", "bibtex", "citation", "references"],
            "weak": ["paper", "research", "academic", "journal"]
        },
        "Other": {
            "strong": [],
            "weak": []
        }
    }
    
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        logger.info(f"LLM Service initialized with model: {model}")
    
    def _analyze_keywords(self, text: str) -> Dict[str, int]:
        """Analyze keyword distribution across categories"""
        text_lower = text.lower()
        scores = {category: 0 for category in self.CATEGORY_KEYWORDS}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            # Strong keyword matches (2 points each)
            for keyword in keywords["strong"]:
                scores[category] += text_lower.count(keyword) * 2
            
            # Weak keyword matches (1 point each)
            for keyword in keywords["weak"]:
                scores[category] += text_lower.count(keyword) * 1
        
        return scores
    
    def _analyze_structure(self, text: str) -> Dict[str, float]:
        """Analyze document structure to infer category"""
        lines = text.split('\n')
        scores = {category: 0.0 for category in self.CATEGORY_KEYWORDS}
        text_lower = text.lower()
        
        # Strong HTML detection - must classify as Frontend
        html_indicators = [
            '<!doctype html',
            '<html',
            '</html>',
            '<head>',
            '</head>',
            '<body>',
            '</body>',
            '<meta',
            '<link rel='
        ]
        html_tag_count = sum(1 for indicator in html_indicators if indicator in text_lower)
        if html_tag_count >= 3:  # If 3+ HTML structural tags present
            scores["FrontendCode"] += 20  # Very high score to override others
        
        # Count HTML tags
        html_tag_patterns = ['<div', '<button', '<input', '<form', '<span', '<p>', '<h1', '<h2', '<h3',
                            '<nav', '<header', '<footer', '<section', '<article', '<script', '<style']
        html_count = sum(text_lower.count(tag) for tag in html_tag_patterns)
        if html_count > 10:
            scores["FrontendCode"] += 10
        elif html_count > 5:
            scores["FrontendCode"] += 5
        
        # Header analysis (more headers = documentation)
        header_count = sum(1 for line in lines if line.strip().startswith('#'))
        if header_count > 5:
            scores["Documentation"] += 3
        
        # Code pattern analysis - check for programming constructs
        code_indicators = ['def ', 'class ', 'import ', 'function', 'return', 'if ', 'for ', 'while ']
        code_lines = sum(1 for line in lines if any(ind in line for ind in code_indicators))
        if code_lines > len(lines) * 0.2:  # 20%+ lines have code patterns
            # Favor BackendCode when code indicators dominate
            scores["BackendCode"] += 4
        
        # Question/Answer analysis
        qa_patterns = ['?', 'question:', 'answer:', 'q:', 'a:', 'what ', 'how ', 'why ']
        qa_count = sum(1 for line in lines if any(pat in line.lower() for pat in qa_patterns))
        if qa_count > len(lines) * 0.15:
            scores["Education"] += 3
        
        # JSON/Schema analysis (API/Documentation)
        if re.search(r'\{.*\}', text) and re.search(r'"[^"]*":\s*', text):
            scores["Documentation"] += 2
        
        # Code block indicators
        if '```' in text or '```python' in text or '```javascript' in text:
            scores["BackendCode"] += 3
        
        # Structured list patterns (documentation)
        if text.count('\n-') > 10:
            scores["Documentation"] += 2
        
        return scores
    
    def _analyze_content_type(self, text: str) -> Dict[str, float]:
        """Analyze specific content patterns and semantic meaning"""
        scores = {category: 0.0 for category in self.CATEGORY_KEYWORDS}
        text_lower = text.lower()
        
        # BackendCode: Server-side logic, APIs, databases
        if re.search(r'\b(flask|django|fastapi|express|spring boot|node\.js)\b', text_lower):
            scores["BackendCode"] += 4
        if re.search(r'\b(sql|select|insert|update|delete|join|where|group by)\b', text_lower):
            scores["BackendCode"] += 3
        if re.search(r'\b(endpoint|route|controller|middleware|authentication|jwt|session)\b', text_lower):
            scores["BackendCode"] += 3
        if re.search(r'\b(pymongo|sqlalchemy|mongoose|sequelize|prisma|orm)\b', text_lower):
            scores["BackendCode"] += 3
        
        # Code: Generic programming (not frontend/backend specific)
        if re.search(r'\b(algorithm|data structure|sorting|searching|recursion)\b', text_lower):
            scores["Code"] += 4
        if re.search(r'\b(debug|debugger|breakpoint|trace|stack trace)\b', text_lower):
            scores["Code"] += 3
        if re.search(r'\b(test|unit test|assert|expect|mock)\b', text_lower):
            scores["Code"] += 3
        if re.search(r'\b(class|object|inheritance|polymorphism|encapsulation)\b', text_lower):
            scores["Code"] += 2
        
        # FrontendCode: UI, HTML, CSS, JavaScript frameworks
        if re.search(r'<(html|head|body|div|button|input|form|nav|header|footer)', text_lower):
            scores["FrontendCode"] += 5
        if re.search(r'\b(onclick|onchange|onclick|event\.prevent|addeventlistener)\b', text_lower):
            scores["FrontendCode"] += 4
        if re.search(r'\b(css|stylesheet|@media|flexbox|grid|padding|margin|border)\b', text_lower):
            scores["FrontendCode"] += 3
        if re.search(r'\b(usestate|useeffect|usecontext|component|props\.|\.render\()\b', text_lower):
            scores["FrontendCode"] += 4
        if re.search(r'\b(bootstrap|tailwind|material-ui|styled-components)\b', text_lower):
            scores["FrontendCode"] += 3
        
        # DataScience: ML, AI, data analysis
        if re.search(r'\b(pandas|numpy|matplotlib|seaborn|plotly)\.', text_lower):
            scores["DataScience"] += 5
        if re.search(r'\b(tensorflow|pytorch|keras|scikit-learn|sklearn)\b', text_lower):
            scores["DataScience"] += 5
        if re.search(r'\b(neural network|deep learning|cnn|rnn|lstm|transformer)\b', text_lower):
            scores["DataScience"] += 4
        if re.search(r'\b(train_test_split|fit|predict|accuracy|precision|recall|f1[- ]score)\b', text_lower):
            scores["DataScience"] += 4
        if re.search(r'\b(dataset|dataframe|feature engineering|preprocessing|normalization)\b', text_lower):
            scores["DataScience"] += 3
        
        # Documentation: Technical docs, guides, API references
        doc_api_hits = 1 if re.search(r'\b(api reference|endpoint documentation|swagger|openapi)\b', text_lower) else 0
        doc_install_hits = 1 if re.search(r'(###?\s+installation|###?\s+usage|###?\s+getting started)', text_lower) else 0
        doc_tutorial_hits = 1 if re.search(r'\b(tutorial|walkthrough|step[- ]by[- ]step|how[- ]to guide)\b', text_lower) else 0
        doc_reqres_hits = 1 if re.search(r'(request:|response:|parameters?:|returns?:)', text_lower) else 0
        documentation_score = doc_api_hits * 5 + doc_install_hits * 4 + doc_tutorial_hits * 3 + doc_reqres_hits * 3

        # Education indicators (prefer Education over Documentation when present)
        edu_indicators = [
            r'\bcurriculum\b', r'\bsyllabus\b', r'\bcourse\b', r'\bmodule\b', r'\blesson\b', r'\bunit\b',
            r'\blecture\b', r'\bassignment\b', r'\bexam\b', r'\bquiz\b', r'\bexercise\b'
        ]
        edu_hits = sum(1 for pat in edu_indicators if re.search(pat, text_lower))
        if documentation_score:
            scores["Documentation"] += documentation_score
            # If educational context detected, boost Education to dominate and slightly dampen Documentation
            if edu_hits:
                scores["Education"] += documentation_score * 1.5 + edu_hits * 2
                scores["Documentation"] -= min(2.0, edu_hits * 0.5)
        
        # Education: Learning materials, Q&A, exercises
        if re.search(r'\b(question|answer|quiz|test|exam|assignment|homework)\s*[:\d]', text_lower):
            scores["Education"] += 5
        if re.search(r'\b(chapter|lesson|module|unit)\s+\d+', text_lower):
            scores["Education"] += 4
        if re.search(r'\b(objective|learning outcome|prerequisite|exercise)\b', text_lower):
            scores["Education"] += 3
        if re.search(r'\b(solve|evaluate|calculate|derive|prove|explain why)\b', text_lower):
            scores["Education"] += 2

        # Field-specific boosts under Education: Database, CyberSecurity, Software, ML, DataScience
        # If educational context words co-occur with these domains, prefer Education over Documentation/DataScience
        has_edu_context = edu_hits > 0 or re.search(r'\b(unit|chapter|lesson|module|lecture|course)\b', text_lower)
        if has_edu_context:
            if re.search(r'\b(sql|database|relational|normalization|transaction|index|join)\b', text_lower):
                scores["Education"] += 4
            if re.search(r'\b(cyber\s*security|cybersecurity|encryption|hashing|firewall|vulnerability|penetration test)\b', text_lower):
                scores["Education"] += 4
            if re.search(r'\b(software engineering|sdlc|requirements|design pattern|testing|version control|git)\b', text_lower):
                scores["Education"] += 4
            if re.search(r'\b(ml|machine learning|supervised|unsupervised|regression|classification|neural network)\b', text_lower):
                scores["Education"] += 4
            if re.search(r'\b(data science|pandas|numpy|analysis|visualization|statistics)\b', text_lower):
                scores["Education"] += 4
        
        # STRONG: Always route Database, Cybersecurity, REST, Software, Test to Education (not Documentation)
        # These are learning topics, not technical API docs
        if re.search(r'\b(database|sql|relational|normalization|transaction|index|join|schema|query|ddl|dml)\b', text_lower):
            scores["Education"] += 8  # Strong boost to override Documentation
            scores["Documentation"] -= 3  # Dampen Documentation classification
        if re.search(r'\b(cyber\s*security|cybersecurity|encryption|hashing|firewall|vulnerability|penetration|attack vectors|network security)\b', text_lower):
            scores["Education"] += 8
            scores["Documentation"] -= 3
        if re.search(r'\b(rest|rest api|restful|http methods|status codes|endpoints?|request|response)\b', text_lower):
            scores["Education"] += 8
            scores["Documentation"] -= 3
        if re.search(r'\b(software engineering|software development|sdlc|design patterns?|architecture|testing|qa|quality assurance)\b', text_lower):
            scores["Education"] += 8
            scores["Documentation"] -= 3
        if re.search(r'\b(test|testing|unit test|integration test|test case|test suite|debugging)\b', text_lower):
            scores["Education"] += 6
            scores["Documentation"] -= 2
        
        # Healthcare: Medical records, clinical data
        if re.search(r'\b(patient|diagnosis|treatment|symptoms?|medication|prescription)\b', text_lower):
            scores["Healthcare"] += 5
        if re.search(r'\b(clinical trial|medical history|vital signs|blood pressure|heart rate)\b', text_lower):
            scores["Healthcare"] += 4
        if re.search(r'\b(dicom|hl7|icd[- ]?10|cpt code|medical imaging)\b', text_lower):
            scores["Healthcare"] += 4
        if re.search(r'\b(doctor|physician|nurse|hospital|clinic|emergency)\b', text_lower):
            scores["Healthcare"] += 2
        
        # Legal: Contracts, agreements, compliance
        if re.search(r'\b(hereby|whereas|pursuant to|in accordance with|aforementioned)\b', text_lower):
            scores["Legal"] += 5
        if re.search(r'\b(contract|agreement|terms and conditions|liability|indemnity)\b', text_lower):
            scores["Legal"] += 4
        if re.search(r'\b(party|parties|shall|clause|section|article|amendment)\b', text_lower):
            scores["Legal"] += 3
        if re.search(r'\b(copyright|patent|trademark|intellectual property|license)\b', text_lower):
            scores["Legal"] += 4
        
        # Finance: Financial statements, reports, analysis
        if re.search(r'\b(revenue|profit|loss|ebitda|balance sheet|income statement)\b', text_lower):
            scores["Finance"] += 5
        if re.search(r'\b(assets?|liabilities|equity|cash flow|fiscal year)\b', text_lower):
            scores["Finance"] += 4
        if re.search(r'\b(investment|stock|dividend|portfolio|return on investment|roi)\b', text_lower):
            scores["Finance"] += 4
        if re.search(r'\b(accounting|audit|financial statement|gaap|ifrs)\b', text_lower):
            scores["Finance"] += 3
        
        # Business: Strategy, operations, management
        if re.search(r'\b(strategy|strategic plan|business model|value proposition)\b', text_lower):
            scores["Business"] += 5
        if re.search(r'\b(marketing|sales|customer acquisition|market share|target audience)\b', text_lower):
            scores["Business"] += 4
        if re.search(r'\b(kpi|metrics|objectives?|milestones?|roadmap)\b', text_lower):
            scores["Business"] += 3
        if re.search(r'\b(stakeholder|management|leadership|organization|team structure)\b', text_lower):
            scores["Business"] += 3
        
        # ResearchPaper: Academic research, papers
        if re.search(r'\b(abstract|introduction|methodology|results?|conclusion|references?)\b', text_lower):
            scores["ResearchPaper"] += 5
        if re.search(r'\b(hypothesis|experiment|empirical|statistical analysis|p[- ]value)\b', text_lower):
            scores["ResearchPaper"] += 4
        if re.search(r'\b(citation|bibliography|doi|journal|peer[- ]review)\b', text_lower):
            scores["ResearchPaper"] += 4
        if re.search(r'\b(et al\.|figure \d+|table \d+|section [ivxlc]+)\b', text_lower):
            scores["ResearchPaper"] += 3
        
        return scores
    
    def _classify_by_analysis(self, text: str) -> Tuple[str, float]:
        """Use multi-strategy analysis to classify content - fast and accurate"""
        keyword_scores = self._analyze_keywords(text)
        structure_scores = self._analyze_structure(text)
        content_scores = self._analyze_content_type(text)
        
        # Combine all scores with strategic weighting
        final_scores = {}
        for category in self.CATEGORY_KEYWORDS:
            final_scores[category] = (
                keyword_scores.get(category, 0) * 1.0 +      # Keywords (1x weight)
                structure_scores.get(category, 0) * 1.5 +    # Structure (1.5x weight)
                content_scores.get(category, 0) * 1.5        # Content patterns (1.5x weight)
            )
        
        # Get best category
        best_category = max(final_scores, key=final_scores.get)
        best_score = final_scores[best_category]
        
        # Filter out "Other" if we have real candidates
        if best_category == "Other" and best_score == 0:
            return "Other", 0.0
        
        logger.debug(f"Classification scores: {final_scores}")
        return best_category, best_score
    
    def classify_content(self, text: str) -> str:
        """Classify content using optimized multi-strategy approach
        
        Strategy:
        1. Fast analysis using keywords, structure, and content patterns
        2. If high confidence (score > 15), return immediately
        3. If low confidence, use LLM for verification
        4. Fallback to analysis if LLM unclear
        
        This optimizes for speed (most docs > 15 score) while maintaining accuracy.
        """
        try:
            # Step 1: Fast content analysis (no LLM needed)
            analysis_category, analysis_score = self._classify_by_analysis(text)
            
            # Special handling: Presentation files (PPTX) with educational indicators
            # Check if content suggests presentation/slides
            text_lower = text.lower()
            has_presentation_indicators = any(ind in text_lower for ind in [
                'slide', 'presentation', 'unit ', 'chapter', 'lesson', 'module', 'lecture'
            ])
            
            # If classified as Code but has presentation indicators, reclassify as Education
            if analysis_category == "Code" and has_presentation_indicators:
                logger.info(f"Reclassifying from Code to Education (presentation detected)")
                analysis_category = "Education"
                analysis_score = 18  # High confidence for Education
            
            # Step 2: High confidence threshold - use analysis result
            if analysis_score > 15:
                logger.info(f"✓ FAST CLASSIFIED (score: {analysis_score:.1f}): {analysis_category}")
                return analysis_category
            
            # Step 3: Low confidence - verify with LLM
            logger.info(f"⚠ Low confidence ({analysis_score:.1f}), using LLM verification...")
            
            prompt = f"""You are a document classifier. Classify into ONE category:

- BackendCode: Python, Java, Node.js, databases, APIs, routes, middleware, server logic
- FrontendCode: React, Vue, Angular, HTML, CSS, JavaScript, UI components, web pages
- Code: General programming, algorithms, data structures, utilities, scripts (not frontend/backend specific)
- DataScience: Machine learning, neural networks, data analysis, pandas, numpy, sklearn, TensorFlow
- Documentation: API docs, tutorials, guides, references, specifications, README
- Education: Questions, exercises, quizzes, tests, courses, learning materials
- Healthcare: Medical documents, patient records, diagnosis, clinical data, DICOM
- Legal: Contracts, agreements, compliance, terms, intellectual property, law
- Finance: Revenue, profits, budgets, ROI, accounting, financial statements
- Business: Strategy, marketing, sales, operations, management, planning
- ResearchPaper: Academic research, methodology, analysis, conclusions, citations
- Other: doesn't fit above

Respond with ONLY the category name.

Document:
{text[:800]}

Category:"""
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.05,
                    "num_predict": 5
                }
            )
            
            raw_response = response['response'].strip().lower()
            first_word = raw_response.split()[0] if raw_response else "other"
            
            category_map = {
                # Backend-specific
                "backend": "BackendCode",
                "backendcode": "BackendCode",
                "server": "BackendCode",
                "api": "BackendCode",
                "database": "BackendCode",
                "endpoint": "BackendCode",
                
                # Frontend-specific
                "frontend": "FrontendCode",
                "frontendcode": "FrontendCode",
                "html": "FrontendCode",
                "webpage": "FrontendCode",
                "ui": "FrontendCode",
                "interface": "FrontendCode",
                "client": "FrontendCode",
                
                # Generic Code
                "code": "Code",
                "programming": "Code",
                "script": "Code",
                "algorithm": "Code",
                "utility": "Code",
                
                # Data Science
                "data science": "DataScience",
                "datascience": "DataScience",
                "machine learning": "DataScience",
                "ml": "DataScience",
                "ai": "DataScience",
                "neural": "DataScience",
                "model": "DataScience",
                
                # Documentation
                "documentation": "Documentation",
                "docs": "Documentation",
                "guide": "Documentation",
                "tutorial": "Documentation",
                "readme": "Documentation",
                "manual": "Documentation",
                
                # Education
                "education": "Education",
                "educational": "Education",
                "learning": "Education",
                "question": "Education",
                "quiz": "Education",
                "exam": "Education",
                "course": "Education",
                
                # Healthcare
                "healthcare": "Healthcare",
                "medical": "Healthcare",
                "clinical": "Healthcare",
                "patient": "Healthcare",
                "diagnosis": "Healthcare",
                
                # Legal
                "legal": "Legal",
                "contract": "Legal",
                "agreement": "Legal",
                "law": "Legal",
                "compliance": "Legal",
                
                # Finance
                "finance": "Finance",
                "financial": "Finance",
                "accounting": "Finance",
                "revenue": "Finance",
                "investment": "Finance",
                
                # Business
                "business": "Business",
                "strategy": "Business",
                "marketing": "Business",
                "sales": "Business",
                "management": "Business",
                "operations": "Business",
                
                # Research
                "research": "ResearchPaper",
                "researchpaper": "ResearchPaper",
                "paper": "ResearchPaper",
                "academic": "ResearchPaper",
                "study": "ResearchPaper",
                
                # Fallback
                "other": "Other"
            }
            
            for key, value in category_map.items():
                if key in first_word:
                    logger.info(f"✓ LLM VERIFIED: {value}")
                    return value
            
            # Step 4: Fallback to analysis if LLM unclear
            logger.info(f"✓ LLM unclear, using analysis: {analysis_category}")
            return analysis_category
            
        except Exception as e:
            logger.error(f"Error classifying content: {e}")
            try:
                analysis_category, _ = self._classify_by_analysis(text)
                return analysis_category
            except:
                return "Other"
    
    def _calculate_confidence(self, query: str, chunks: List[dict]) -> float:
        """Calculate confidence score (0-100) for the answer"""
        if not chunks:
            return 0.0
        
        # Similarity is already normalized (0-1) from database
        avg_similarity = sum(chunk.get('similarity', 0) for chunk in chunks) / len(chunks)
        
        # More chunks = more confidence
        chunk_bonus = min(len(chunks) / 5.0, 1.0)
        
        # Distance-based confidence (lower distance = higher confidence)
        avg_distance = sum(chunk.get('distance', 2.0) for chunk in chunks) / len(chunks)
        distance_confidence = max(0, 1.0 - (avg_distance / 2.0))
        
        # Combined confidence: higher weight to similarity + distance
        confidence = (avg_similarity * 0.5 + distance_confidence * 0.3 + chunk_bonus * 0.2)
        
        # Ensure we have reasonable minimum confidence when we have good results
        # If similarity > 0.3 and we have chunks, minimum 40% confidence
        if avg_similarity > 0.3 and len(chunks) > 0:
            confidence = max(0.40, confidence)
        
        confidence_score = int(confidence * 100)
        return max(0, min(100, confidence_score))
    
    def _get_confidence_level(self, score: int) -> str:
        """Get confidence level label"""
        if score >= 75:
            return "🟢 HIGH"
        elif score >= 40:
            return "🟡 MEDIUM"
        else:
            return "🔴 LOW"
    
    def generate_response(self, query: str, context_chunks: List[dict]) -> Tuple[str, List[str], float, List[dict]]:
        """Generate response STRICTLY from documents only - no external knowledge"""
        
        if not context_chunks:
            # No documents found - cannot answer
            return "I don't have this information in your documents. Please upload relevant documents or ask questions about the documents you've provided.", [], 0, []
        
        context_chunks = context_chunks[:5]
        confidence_score = self._calculate_confidence(query, context_chunks)
        confidence_level = self._get_confidence_level(confidence_score)
        
        source_snippets = []
        for i, chunk in enumerate(context_chunks, 1):
            snippet = {
                'id': i,
                'filename': chunk['filename'],
                'category': chunk.get('category', 'Unknown'),
                'text': chunk['text'][:300] + '...' if len(chunk['text']) > 300 else chunk['text'],
                'similarity': chunk.get('similarity', 0),
                'relevance_pct': int(chunk.get('similarity', 0) * 100)
            }
            source_snippets.append(snippet)
        
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source_info = f"[Source {i}: {chunk['filename']}]"
            context_parts.append(f"{source_info}\n{chunk['text']}\n")
        
        context_text = "\n".join(context_parts)
        
        # STRICT DOCUMENT-ONLY PROMPT - No external knowledge allowed
        full_prompt = f"""You are a helpful AI assistant that answers questions EXCLUSIVELY and STRICTLY based on the provided documents.

CRITICAL RULES:
1. ONLY answer using information from the documents below
2. Do NOT use any external knowledge, general knowledge, or information from training data
3. If the answer is NOT in the documents, respond: "I don't have this information in the provided documents."
4. Do NOT make up, infer, or assume information
5. Always cite which document the information comes from
6. Provide detailed, comprehensive answers using ALL relevant information from the documents
7. Include all types, categories, characteristics, and details mentioned in the documents
8. Use bullet points, numbering, or clear formatting when listing multiple items

Documents:
{context_text}

Question: {query}

Answer ONLY based on the documents above. Provide a comprehensive, detailed answer with all relevant information. If information is not in documents, say so clearly:"""
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 1024,
                    "num_ctx": 4096,
                    "repeat_penalty": 1.1,
                    "num_thread": 8,
                }
            )
            
            answer = response['response'].strip()
            
            # Check if LLM says information is not in documents
            no_info_phrases = [
                "don't have this information",
                "not in the provided documents",
                "not in the documents",
                "cannot find this information",
                "no information about",
                "not mentioned in the documents",
                "not available in the documents"
            ]
            
            is_no_info = any(phrase in answer.lower() for phrase in no_info_phrases)
            
            if is_no_info:
                # Don't add sources/confidence if information not found
                return answer, [], 0, []
            
            cited_files = list(set([chunk['filename'] for chunk in context_chunks]))
            
            if cited_files:
                answer += f"\n\n📊 Confidence: {confidence_level} ({confidence_score}%)"
                answer += f"\n📄 Sources: {', '.join(cited_files)}"
            
            return answer, cited_files, confidence_score, source_snippets
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's an Ollama connection error
            if "connection" in error_msg or "ollama" in error_msg or "failed" in error_msg:
                logger.warning(f"Ollama unavailable: {e}")
                # Return message asking to start Ollama
                return "I cannot answer right now because Ollama is not running. Please start Ollama to get AI-powered answers from your documents.", [], 0, []
            
            else:
                logger.error(f"Error generating response: {e}")
                return f"Error: Unable to generate response. {str(e)}", [], 0, []
    
    def check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            ollama.list()
            return True
        except:
            return False
