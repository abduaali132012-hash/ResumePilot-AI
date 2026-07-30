import unittest

from app import AI_OUTPUT_HEADERS, SAMPLE_AI_RESPONSE, extract_section, validate_ai_response_sections


class ParserHelperTests(unittest.TestCase):
    def test_validate_ai_response_sections_with_complete_response(self):
        missing = validate_ai_response_sections(SAMPLE_AI_RESPONSE, AI_OUTPUT_HEADERS)
        self.assertEqual(missing, [])

    def test_extract_section_returns_expected_content(self):
        summary = extract_section(SAMPLE_AI_RESPONSE, "### RESUME SUMMARY")
        self.assertIn("Experienced marketing professional", summary)

        cover_letter = extract_section(SAMPLE_AI_RESPONSE, "### TAILORED COVER LETTER")
        self.assertTrue(cover_letter.startswith("Dear Hiring Manager"))

    def test_extract_section_returns_fallback_when_header_missing(self):
        invalid_response = "### RESUME SUMMARY\nExample summary only."
        result = extract_section(invalid_response, "### CORE STRENGTHS")
        self.assertIn("Unable to extract the '### CORE STRENGTHS' section", result)

    def test_validate_ai_response_sections_detects_missing_headers(self):
        partial_response = "### RESUME SUMMARY\nExample summary only.\n### CORE STRENGTHS\n- Skill"
        missing = validate_ai_response_sections(partial_response, AI_OUTPUT_HEADERS)
        self.assertIn("### CRITICAL WEAKNESSES", missing)
        self.assertIn("### INTERVIEW PREPARATION", missing)
        self.assertIn("### RESUME REWRITE SUGGESTIONS", missing)
        self.assertIn("### CAREER COACH GUIDANCE", missing)
        self.assertIn("### TAILORED COVER LETTER", missing)


if __name__ == "__main__":
    unittest.main()
