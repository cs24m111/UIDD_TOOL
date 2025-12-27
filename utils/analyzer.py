"""
Compliance analysis utilities for Indian IT Rules 2021
"""
import re
from typing import Dict, List, Tuple
from difflib import SequenceMatcher


class ComplianceAnalyzer:
    """Analyzes text content for IT Rules 2021 compliance"""

    def __init__(self):
        # Official definition of synthetically generated information
        self.official_definition = (
            "Information that is artificially or algorithmically created, generated, "
            "modified or altered using a computer resource, in a manner that appears "
            "reasonably authentic or true"
        )

        # Keywords for each rule
        self.rule_keywords = {
            'rule_2_1_wa': {
                'required': ['synthetic', 'generated', 'artificial', 'algorithmic'],
                'definition_terms': ['information', 'created', 'computer', 'authentic', 'true']
            },
            'rule_4_2': {
                'required': ['automated', 'tool', 'detect', 'AI', 'synthetic', 'harmful'],
                'patterns': [
                    r'automated\s+tool',
                    r'detection\s+(?:tool|system|mechanism)',
                    r'AI\s+(?:content|detection)',
                    r'synthetic\s+(?:content|detection)'
                ]
            },
            'rule_4_4': {
                'required': ['complaint', 'grievance', 'AI', 'synthetic'],
                'patterns': [
                    r'complaint\s+(?:mechanism|handling|process)',
                    r'grievance\s+(?:mechanism|redressal)',
                    r'(?:AI|synthetic)\s+content'
                ]
            },
            'rule_3_1_b': {
                'required': ['prohibited', 'deepfake', 'misleading', 'section 79'],
                'patterns': [
                    r'deepfake',
                    r'misleading\s+(?:information|content)',
                    r'section\s+79',
                    r'prohibited\s+content'
                ]
            },
            'rule_3_3': {
                'label': ['label', 'metadata', 'identifier', 'mark'],
                'surface_area': ['10%', 'ten percent', 'surface area', 'duration'],
                'immediate': ['immediate', 'readily', 'easily', 'identifiable'],
                'prohibition': ['prohibit', 'prevent', 'not allow', 'removal', 'modification']
            },
            'rule_4_1a': {
                'declaration': ['declaration', 'user', 'authentic', 'synthetic'],
                'verification': ['verification', 'technical', 'measure'],
                'labeling': ['label', 'ensure', 'synthetic']
            }
        }

    def check_rule_2_1_wa(self, text: str) -> Dict:
        """
        Check Rule 2(1)(wa) - Definition of synthetically generated information

        Args:
            text: Privacy policy text

        Returns:
            Dictionary with compliance result
        """
        text_lower = text.lower()
        score = 0
        evidence = []
        findings = []

        # Check for keyword presence (20% of score)
        keywords_found = []
        for keyword in self.rule_keywords['rule_2_1_wa']['required']:
            if keyword in text_lower:
                keywords_found.append(keyword)

        keyword_score = (len(keywords_found) / len(self.rule_keywords['rule_2_1_wa']['required'])) * 20
        score += keyword_score

        if keywords_found:
            findings.append(f"Found {len(keywords_found)}/4 required keywords: {', '.join(keywords_found)}")

        # Search for definition-like patterns (80% of score)
        definition_patterns = [
            r'(?:synthetic[a-z]*\s+generated\s+information|artificially\s+(?:created|generated)).*?(?:computer|algorithm|AI).*?(?:authentic|true)',
            r'information.*?(?:artificial|algorithmic)[a-z]*\s+(?:created|generated|modified).*?computer',
            r'(?:AI|artificial|algorithmic)[a-z\s]*(?:generated|created).*?(?:authentic|appears)',
        ]

        best_match_score = 0
        best_match_text = ""

        # Find sentences containing multiple definition terms
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Count definition terms in sentence
            term_count = sum(1 for term in self.rule_keywords['rule_2_1_wa']['definition_terms']
                           if term in sentence_lower)

            keyword_count = sum(1 for kw in self.rule_keywords['rule_2_1_wa']['required']
                              if kw in sentence_lower)

            if term_count >= 3 or keyword_count >= 2:
                # Calculate similarity with official definition
                similarity = self.calculate_similarity(sentence_lower, self.official_definition.lower())

                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match_text = sentence.strip()

        # Award points based on similarity
        if best_match_score > 0.6:
            definition_score = 80
            findings.append(f"Found highly similar definition (similarity: {best_match_score:.2%})")
            evidence.append(best_match_text)
        elif best_match_score > 0.4:
            definition_score = 60
            findings.append(f"Found partially matching definition (similarity: {best_match_score:.2%})")
            evidence.append(best_match_text)
        elif best_match_score > 0.2:
            definition_score = 30
            findings.append(f"Found weak definition match (similarity: {best_match_score:.2%})")
            evidence.append(best_match_text)
        else:
            definition_score = 0
            findings.append("No clear definition of synthetically generated information found")

        score += definition_score

        return {
            'rule': 'Rule 2(1)(wa)',
            'description': 'Definition of Synthetically Generated Information',
            'score': min(100, score),
            'status': 'Pass' if score >= 70 else ('Partial' if score >= 40 else 'Fail'),
            'findings': findings,
            'evidence': evidence,
            'recommendation': self._get_recommendation_2_1_wa(score)
        }

    def check_rule_4_2(self, text: str) -> Dict:
        """
        Check Rule 4(2) - Automated tools for detection

        Args:
            text: Privacy policy text

        Returns:
            Dictionary with compliance result
        """
        text_lower = text.lower()
        score = 0
        evidence = []
        findings = []

        # Check for patterns
        patterns_found = 0
        for pattern in self.rule_keywords['rule_4_2']['patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                patterns_found += 1
                context = self._get_context(text, match.start(), match.end())
                evidence.append(context)
                break  # Only need one match per pattern

        # Check for required keywords
        keywords_found = sum(1 for kw in self.rule_keywords['rule_4_2']['required']
                           if kw in text_lower)

        # Calculate score
        pattern_score = min(60, patterns_found * 20)
        keyword_score = min(40, keywords_found * 10)
        score = pattern_score + keyword_score

        findings.append(f"Found {patterns_found} pattern matches for automated detection tools")
        findings.append(f"Found {keywords_found}/6 relevant keywords")

        if patterns_found == 0:
            findings.append("No mention of automated detection tools found")

        return {
            'rule': 'Rule 4(2)',
            'description': 'Deployment of Automated Tools for Detection',
            'score': min(100, score),
            'status': 'Pass' if score >= 60 else ('Partial' if score >= 30 else 'Fail'),
            'findings': findings,
            'evidence': evidence[:3],  # Limit evidence
            'recommendation': self._get_recommendation_4_2(score)
        }

    def check_rule_4_4(self, text: str) -> Dict:
        """
        Check Rule 4(4) - Complaint handling mechanism

        Args:
            text: Privacy policy text

        Returns:
            Dictionary with compliance result
        """
        text_lower = text.lower()
        score = 0
        evidence = []
        findings = []

        # Check for complaint mechanism
        complaint_keywords = ['complaint', 'grievance', 'report', 'appeal']
        complaint_found = sum(1 for kw in complaint_keywords if kw in text_lower)

        # Check for AI/synthetic content mention in complaint context
        ai_keywords = ['ai', 'synthetic', 'generated', 'deepfake', 'artificial']

        # Find sections mentioning complaints
        complaint_sections = []
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in complaint_keywords):
                complaint_sections.append(sentence)

        # Check if complaint sections mention AI content
        ai_in_complaint = 0
        for section in complaint_sections:
            section_lower = section.lower()
            if any(kw in section_lower for kw in ai_keywords):
                ai_in_complaint += 1
                evidence.append(section.strip())

        # Scoring
        if complaint_found > 0:
            score += 40
            findings.append(f"Found complaint/grievance mechanism mentioned {complaint_found} times")

        if ai_in_complaint > 0:
            score += 60
            findings.append(f"Found {ai_in_complaint} mentions of AI/synthetic content in complaint handling")
        else:
            findings.append("Complaint mechanism does not specifically mention AI-generated content")

        return {
            'rule': 'Rule 4(4)',
            'description': 'Complaint Handling for AI-Generated Content',
            'score': min(100, score),
            'status': 'Pass' if score >= 70 else ('Partial' if score >= 40 else 'Fail'),
            'findings': findings,
            'evidence': evidence[:2],
            'recommendation': self._get_recommendation_4_4(score)
        }

    def check_rule_3_1_b(self, text: str) -> Dict:
        """
        Check Rule 3(1)(b) Proviso - Prohibited content including harmful AI content

        Args:
            text: Privacy policy text

        Returns:
            Dictionary with compliance result
        """
        text_lower = text.lower()
        score = 0
        evidence = []
        findings = []

        # Check for prohibited content mention
        prohibited_found = 'prohibited' in text_lower or 'not permitted' in text_lower or 'not allowed' in text_lower

        # Check for specific harmful AI content types
        harmful_ai_types = {
            'deepfake': r'deepfake',
            'misleading': r'misleading.*?(?:information|content)',
            'manipulated': r'manipulated.*?(?:media|content|information)',
            'section_79': r'section\s+79'
        }

        types_found = {}
        for content_type, pattern in harmful_ai_types.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                types_found[content_type] = len(matches)
                context = self._get_context(text, matches[0].start(), matches[0].end())
                evidence.append(context)

        # Scoring
        if prohibited_found:
            score += 30
            findings.append("Platform mentions prohibited content")

        if 'deepfake' in types_found:
            score += 35
            findings.append("Deepfakes explicitly mentioned as prohibited")

        if 'misleading' in types_found or 'manipulated' in types_found:
            score += 20
            findings.append("Misleading/manipulated AI content mentioned")

        if 'section_79' in types_found:
            score += 15
            findings.append("Section 79 immunity mentioned")

        if not types_found:
            findings.append("No specific mention of harmful AI-generated content types")

        return {
            'rule': 'Rule 3(1)(b) Proviso',
            'description': 'Prohibition of Harmful AI-Generated Content',
            'score': min(100, score),
            'status': 'Pass' if score >= 70 else ('Partial' if score >= 40 else 'Fail'),
            'findings': findings,
            'evidence': evidence[:3],
            'recommendation': self._get_recommendation_3_1_b(score)
        }

    def check_rule_3_3(self, text: str) -> Dict:
        """
        Check Rule 3(3) - Due diligence for synthetic content labeling

        Args:
            text: Privacy policy text

        Returns:
            Dictionary with compliance result
        """
        text_lower = text.lower()
        evidence = []
        findings = []

        # Four requirements (25% each)
        requirements = {
            'label_required': False,
            'surface_area': False,
            'immediate_identification': False,
            'prohibition_modification': False
        }

        # 1. Check for labeling requirement (25%)
        label_keywords = self.rule_keywords['rule_3_3']['label']
        label_mentions = sum(1 for kw in label_keywords if kw in text_lower)

        if label_mentions >= 2:
            requirements['label_required'] = True
            findings.append("Platform requires labeling/metadata for AI content")

            # Find evidence
            sentences = re.split(r'[.!?]\s+', text)
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in label_keywords):
                    evidence.append(sentence.strip())
                    break

        # 2. Check for 10% surface area/duration requirement (25%)
        surface_patterns = [
            r'10\s*%',
            r'ten\s+percent',
            r'surface\s+area',
            r'duration'
        ]

        for pattern in surface_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                requirements['surface_area'] = True
                findings.append("10% surface area/duration requirement mentioned")
                break

        # 3. Check for immediate identification (25%)
        immediate_keywords = self.rule_keywords['rule_3_3']['immediate']
        if any(kw in text_lower for kw in immediate_keywords):
            requirements['immediate_identification'] = True
            findings.append("Immediate identification requirement mentioned")

        # 4. Check for prohibition of modification/removal (25%)
        prohibition_keywords = self.rule_keywords['rule_3_3']['prohibition']
        prohibition_count = sum(1 for kw in prohibition_keywords if kw in text_lower)

        if prohibition_count >= 2 and ('removal' in text_lower or 'modification' in text_lower):
            requirements['prohibition_modification'] = True
            findings.append("Prohibition of label modification/removal mentioned")

        # Calculate score
        score = sum(25 for req in requirements.values() if req)

        if not any(requirements.values()):
            findings.append("No specific labeling requirements for synthetic content found")

        return {
            'rule': 'Rule 3(3)',
            'description': 'Due Diligence - Synthetic Content Labeling Requirements',
            'score': score,
            'status': 'Pass' if score >= 75 else ('Partial' if score >= 50 else 'Fail'),
            'findings': findings,
            'evidence': evidence[:2],
            'sub_requirements': requirements,
            'recommendation': self._get_recommendation_3_3(score, requirements)
        }

    def check_rule_4_1a(self, text: str) -> Dict:
        """
        Check Rule 4(1A) - SSMI requirements (50 lakh+ users)

        Args:
            text: Privacy policy text

        Returns:
            Dictionary with compliance result
        """
        text_lower = text.lower()
        evidence = []
        findings = []

        # Three requirements (33.33% each)
        requirements = {
            'user_declaration': False,
            'technical_verification': False,
            'synthetic_labeling': False
        }

        # 1. User declaration (33.33%)
        declaration_keywords = self.rule_keywords['rule_4_1a']['declaration']
        declaration_count = sum(1 for kw in declaration_keywords if kw in text_lower)

        if declaration_count >= 2:
            requirements['user_declaration'] = True
            findings.append("User declaration for authentic vs synthetic content mentioned")

            # Find evidence
            sentences = re.split(r'[.!?]\s+', text)
            for sentence in sentences:
                if 'declaration' in sentence.lower() or 'declare' in sentence.lower():
                    evidence.append(sentence.strip())
                    break

        # 2. Technical verification (33.33%)
        verification_keywords = self.rule_keywords['rule_4_1a']['verification']
        verification_count = sum(1 for kw in verification_keywords if kw in text_lower)

        if verification_count >= 2:
            requirements['technical_verification'] = True
            findings.append("Technical verification measures mentioned")

        # 3. Synthetic content labeling (33.33%)
        labeling_keywords = self.rule_keywords['rule_4_1a']['labeling']
        labeling_count = sum(1 for kw in labeling_keywords if kw in text_lower)

        if labeling_count >= 2 and 'synthetic' in text_lower:
            requirements['synthetic_labeling'] = True
            findings.append("Ensures synthetic content labeling")

        # Calculate score
        score = sum(33.33 for req in requirements.values() if req)

        # Check if platform even mentions being SSMI or having 50 lakh users
        ssmi_indicators = ['50 lakh', 'significant social media', 'ssmi', '5 million']
        is_ssmi_mentioned = any(indicator in text_lower for indicator in ssmi_indicators)

        if is_ssmi_mentioned:
            findings.append("Platform identifies as SSMI (50 lakh+ users)")

        if not any(requirements.values()):
            findings.append("No SSMI-specific requirements found")

        return {
            'rule': 'Rule 4(1A)',
            'description': 'SSMI Requirements (50 Lakh+ Users)',
            'score': score,
            'status': 'Pass' if score >= 70 else ('Partial' if score >= 50 else 'Fail'),
            'findings': findings,
            'evidence': evidence[:2],
            'sub_requirements': requirements,
            'is_ssmi_mentioned': is_ssmi_mentioned,
            'recommendation': self._get_recommendation_4_1a(score, requirements)
        }

    def analyze_compliance(self, privacy_policy_text: str) -> Dict:
        """
        Perform complete compliance analysis

        Args:
            privacy_policy_text: Full privacy policy text

        Returns:
            Dictionary with all compliance results
        """
        results = {
            'rule_2_1_wa': self.check_rule_2_1_wa(privacy_policy_text),
            'rule_4_2': self.check_rule_4_2(privacy_policy_text),
            'rule_4_4': self.check_rule_4_4(privacy_policy_text),
            'rule_3_1_b': self.check_rule_3_1_b(privacy_policy_text),
            'rule_3_3': self.check_rule_3_3(privacy_policy_text),
            'rule_4_1a': self.check_rule_4_1a(privacy_policy_text)
        }

        # Calculate overall score
        total_score = sum(result['score'] for result in results.values())
        overall_score = total_score / 6

        # Determine overall status
        if overall_score >= 70:
            overall_status = 'Compliant'
            status_color = 'success'
        elif overall_score >= 40:
            overall_status = 'Partially Compliant'
            status_color = 'warning'
        else:
            overall_status = 'Non-Compliant'
            status_color = 'danger'

        return {
            'overall_score': round(overall_score, 2),
            'overall_status': overall_status,
            'status_color': status_color,
            'rules': results,
            'summary': self._generate_summary(results, overall_score)
        }

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using SequenceMatcher"""
        return SequenceMatcher(None, text1, text2).ratio()

    def _get_context(self, text: str, start: int, end: int, context_size: int = 150) -> str:
        """Extract context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        return "..." + text[context_start:context_end].strip() + "..."

    def _generate_summary(self, results: Dict, overall_score: float) -> str:
        """Generate executive summary"""
        passed = sum(1 for r in results.values() if r['status'] == 'Pass')
        partial = sum(1 for r in results.values() if r['status'] == 'Partial')
        failed = sum(1 for r in results.values() if r['status'] == 'Fail')

        summary = f"Overall Compliance Score: {overall_score:.2f}% | "
        summary += f"Passed: {passed}/6 | Partial: {partial}/6 | Failed: {failed}/6"

        return summary

    # Recommendation methods
    def _get_recommendation_2_1_wa(self, score: float) -> str:
        if score >= 70:
            return "Definition is adequate and compliant."
        return "Add clear definition: 'Synthetically Generated Information means information that is artificially or algorithmically created, generated, modified or altered using a computer resource, in a manner that appears reasonably authentic or true.'"

    def _get_recommendation_4_2(self, score: float) -> str:
        if score >= 60:
            return "Automated detection tools are adequately mentioned."
        return "Explicitly mention deployment of automated tools/systems for detecting harmful synthetic content, including AI-powered detection mechanisms."

    def _get_recommendation_4_4(self, score: float) -> str:
        if score >= 70:
            return "Complaint mechanism adequately covers AI-generated content."
        return "Ensure complaint/grievance mechanism explicitly states that complaints about AI-generated/synthetic content will be handled with same priority as other content."

    def _get_recommendation_3_1_b(self, score: float) -> str:
        if score >= 70:
            return "Prohibited content policy adequately covers harmful AI content."
        return "Explicitly list deepfakes, misleading AI-generated content, and manipulated media as prohibited content. Mention that removal maintains Section 79 safe harbor protection."

    def _get_recommendation_3_3(self, score: float, requirements: Dict) -> str:
        missing = [k.replace('_', ' ').title() for k, v in requirements.items() if not v]
        if not missing:
            return "Labeling requirements are comprehensive."
        return f"Add requirements for: {', '.join(missing)}. Ensure labels cover 10% surface area, enable immediate identification, and prohibit modification/removal."

    def _get_recommendation_4_1a(self, score: float, requirements: Dict) -> str:
        missing = [k.replace('_', ' ').title() for k, v in requirements.items() if not v]
        if not missing:
            return "SSMI requirements are adequately addressed."
        return f"If platform has 50 lakh+ users, add: {', '.join(missing)}. Obtain user declarations, deploy technical verification, and ensure synthetic content labeling."
