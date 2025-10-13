"""
Comprehensive Unit Tests for Bias Detection Service
Phase 0.5 Security Implementation - Brazilian Legal Compliance
"""

from datetime import datetime

import pytest

from app.services.bias_detection_service import (
    BiasDetectionResult,
    BiasDetectionService,
    BiasSeverity,
    FairnessMetrics,
)


class TestBiasDetectionService:
    """Test suite for BiasDetectionService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.bias_service = BiasDetectionService()

    def test_initialization(self):
        """Test service initialization."""
        assert self.bias_service is not None
        assert hasattr(self.bias_service, "protected_characteristics")
        assert hasattr(self.bias_service, "pii_patterns")
        assert hasattr(self.bias_service, "bias_keywords")
        assert len(self.bias_service.protected_characteristics) > 0

    def test_pii_detection_cpf(self):
        """Test CPF detection."""
        text = "Meu CPF é 123.456.789-00 para contato"
        pii = self.bias_service.detect_pii(text)

        assert "cpf" in pii
        assert "123.456.789-00" in pii["cpf"]

    def test_pii_detection_rg(self):
        """Test RG detection."""
        text = "RG: 12.345.678-9 identificação"
        pii = self.bias_service.detect_pii(text)

        assert "rg" in pii
        assert "12.345.678-9" in pii["rg"]

    def test_pii_detection_phone(self):
        """Test phone number detection."""
        text = "Telefone: (11) 98765-4321 ou 21987654321"
        pii = self.bias_service.detect_pii(text)

        assert "phone" in pii
        assert len(pii["phone"]) >= 1

    def test_pii_detection_email(self):
        """Test email detection."""
        text = "Entre em contato: joao.silva@email.com.br"
        pii = self.bias_service.detect_pii(text)

        assert "email" in pii
        assert "joao.silva@email.com.br" in pii["email"]

    def test_pii_detection_address(self):
        """Test address detection."""
        text = "Moro na Rua das Flores, 123, apto 45, São Paulo"
        pii = self.bias_service.detect_pii(text)

        assert "address" in pii

    def test_pii_detection_birth_date(self):
        """Test birth date detection."""
        text = "Nascido em 15/03/1985 ou 1985-03-15"
        pii = self.bias_service.detect_pii(text)

        assert "birth_date" in pii
        assert len(pii["birth_date"]) >= 1

    def test_protected_characteristics_detection_age(self):
        """Test age detection."""
        text = "Tenho 35 anos de idade e nasci em 1988"
        detected = self.bias_service.detect_protected_characteristics(text)

        assert "age" in detected

    def test_protected_characteristics_detection_gender(self):
        """Test gender detection."""
        text = "Masculino, sou homem e trabalho como engenheiro"
        detected = self.bias_service.detect_protected_characteristics(text)

        assert "gender" in detected

    def test_protected_characteristics_detection_race(self):
        """Test race/ethnicity detection."""
        text = "Sou negro, declarado como preto no formulário"
        detected = self.bias_service.detect_protected_characteristics(text)

        assert "race_ethnicity" in detected

    def test_protected_characteristics_detection_disability(self):
        """Test disability detection."""
        text = "Pessoa com deficiência (PCD), cadeirante"
        detected = self.bias_service.detect_protected_characteristics(text)

        assert "disability" in detected

    def test_protected_characteristics_detection_marital_status(self):
        """Test marital status detection."""
        text = "Estado civil: casado, com dois filhos"
        detected = self.bias_service.detect_protected_characteristics(text)

        assert "marital_status" in detected

    def test_protected_characteristics_detection_religion(self):
        """Test religion detection."""
        text = "Religião: católico, praticante"
        detected = self.bias_service.detect_protected_characteristics(text)

        assert "religion" in detected

    def test_protected_characteristics_detection_employment_gaps(self):
        """Test employment gaps detection."""
        text = "Fiquei parado por 6 meses entre empregos"
        detected = self.bias_service.detect_protected_characteristics(text)

        assert "employment_gaps" in detected

    def test_bias_keywords_detection_age_bias(self):
        """Test age bias keywords detection."""
        text = "Candidato muito jovem, porém experiente demais para a vaga"
        bias = self.bias_service.detect_bias_keywords(text)

        assert "age_bias" in bias
        assert len(bias["age_bias"]) >= 1

    def test_bias_keywords_detection_gender_bias(self):
        """Test gender bias keywords detection."""
        text = "Procuramos homem para liderança e mulher para suporte"
        bias = self.bias_service.detect_bias_keywords(text)

        assert "gender_bias" in bias
        assert len(bias["gender_bias"]) >= 1

    def test_bias_keywords_detection_racial_bias(self):
        """Test racial bias keywords detection."""
        text = "Boa aparência profissional necessária para o cargo"
        bias = self.bias_service.detect_bias_keywords(text)

        assert "racial_bias" in bias
        assert len(bias["racial_bias"]) >= 1

    def test_bias_risk_score_calculation(self):
        """Test bias risk score calculation."""
        protected_chars = ["age", "gender"]
        bias_keywords = {"age_bias": ["jovem"], "gender_bias": ["homem"]}
        pii_detected = {"cpf": ["123.456.789-00"]}

        risk_score, severity = self.bias_service.calculate_bias_risk_score(
            protected_chars, bias_keywords, pii_detected
        )

        assert 0 <= risk_score <= 1
        assert severity in list(BiasSeverity)
        assert risk_score > 0.5  # Should be medium-high risk

    def test_bias_risk_score_low_risk(self):
        """Test bias risk score calculation for low risk."""
        protected_chars = []
        bias_keywords = {}
        pii_detected = {}

        risk_score, severity = self.bias_service.calculate_bias_risk_score(
            protected_chars, bias_keywords, pii_detected
        )

        assert risk_score < 0.4
        assert severity == BiasSeverity.LOW

    def test_bias_risk_score_critical_risk(self):
        """Test bias risk score calculation for critical risk."""
        protected_chars = ["age", "gender", "race_ethnicity", "disability"]
        bias_keywords = {
            "age_bias": ["jovem", "velho"],
            "gender_bias": ["homem", "mulher"],
            "racial_bias": ["aparência"],
            "discriminatory": ["brasileiro", "nacionalidade"],
        }
        pii_detected = {"cpf": ["123.456.789-00"], "email": ["test@email.com"]}

        risk_score, severity = self.bias_service.calculate_bias_risk_score(
            protected_chars, bias_keywords, pii_detected
        )

        assert risk_score > 0.8
        assert severity == BiasSeverity.CRITICAL

    def test_analyze_text_bias_comprehensive(self):
        """Test comprehensive text bias analysis."""
        text = """
        João Silva, 35 anos, CPF: 123.456.789-00
        Estado civil: casado
        Telefone: (11) 98765-4321
        Email: joao.silva@email.com
        Engenheiro mecânico, 10 anos de experiência
        """

        result = self.bias_service.analyze_text_bias(text, "resume")

        assert isinstance(result, BiasDetectionResult)
        assert result.has_bias
        assert result.severity in [s for s in BiasSeverity]
        assert len(result.detected_characteristics) > 0
        assert len(result.pii_detected) > 0
        assert result.confidence_score > 0
        assert len(result.explanation) > 0
        assert len(result.recommendations) > 0
        assert result.requires_human_review

    def test_analyze_text_bias_no_bias(self):
        """Test text bias analysis with no bias detected."""
        text = """
        Engenheiro de software com experiência em desenvolvimento
        de aplicações web usando Python e JavaScript.
        Conhecimentos em bancos de dados e APIs REST.
        """

        result = self.bias_service.analyze_text_bias(text, "resume")

        assert isinstance(result, BiasDetectionResult)
        assert not result.has_bias
        assert result.severity == BiasSeverity.LOW
        assert len(result.detected_characteristics) == 0
        assert len(result.pii_detected) == 0
        assert result.confidence_score < 0.5
        assert not result.requires_human_review

    def test_should_block_processing_critical(self):
        """Test processing blocking for critical bias."""
        bias_result = BiasDetectionResult(
            has_bias=True,
            severity=BiasSeverity.CRITICAL,
            detected_characteristics=["age", "gender"],
            confidence_score=0.9,
            explanation="Critical bias detected",
            recommendations=["Remove personal info"],
            pii_detected={"cpf": ["123.456.789-00"]},
            requires_human_review=True,
        )

        should_block = self.bias_service.should_block_processing(bias_result)
        assert should_block

    def test_should_block_processing_high_with_pii(self):
        """Test processing blocking for high bias with PII."""
        bias_result = BiasDetectionResult(
            has_bias=True,
            severity=BiasSeverity.HIGH,
            detected_characteristics=["age"],
            confidence_score=0.7,
            explanation="High bias detected",
            recommendations=["Remove age info"],
            pii_detected={"cpf": ["123.456.789-00"]},
            requires_human_review=True,
        )

        should_block = self.bias_service.should_block_processing(bias_result)
        assert should_block

    def test_should_block_processing_medium(self):
        """Test processing not blocked for medium bias."""
        bias_result = BiasDetectionResult(
            has_bias=True,
            severity=BiasSeverity.MEDIUM,
            detected_characteristics=["age"],
            confidence_score=0.5,
            explanation="Medium bias detected",
            recommendations=["Review age references"],
            pii_detected={},
            requires_human_review=False,
        )

        should_block = self.bias_service.should_block_processing(bias_result)
        assert not should_block

    def test_create_anti_discrimination_prompt_scoring(self):
        """Test anti-discrimination prompt creation for scoring."""
        prompt = self.bias_service.create_anti_discrimination_prompt("scoring")

        assert "REGRAS ANTI-DISCRIMINAÇÃO" in prompt
        assert "NÃO CONSIDERAR" in prompt
        assert "idade, gênero, raça" in prompt
        assert "Constituição Federal" in prompt
        assert "ESPECÍFICO PARA PONTUAÇÃO" in prompt

    def test_create_anti_discrimination_prompt_analysis(self):
        """Test anti-discrimination prompt creation for analysis."""
        prompt = self.bias_service.create_anti_discrimination_prompt("analysis")

        assert "REGRAS ANTI-DISCRIMINAÇÃO" in prompt
        assert "ESPECÍFICO PARA ANÁLISE" in prompt
        assert "identificar e ignorar informações não relevantes" in prompt

    def test_create_anti_discrimination_prompt_improvement(self):
        """Test anti-discrimination prompt creation for improvement."""
        prompt = self.bias_service.create_anti_discrimination_prompt("improvement")

        assert "REGRAS ANTI-DISCRIMINAÇÃO" in prompt
        assert "ESPECÍFICO PARA MELHORIA" in prompt
        assert "melhorar apenas aspectos profissionais" in prompt

    def test_create_bias_report(self):
        """Test bias report creation."""
        bias_result = BiasDetectionResult(
            has_bias=True,
            severity=BiasSeverity.HIGH,
            detected_characteristics=["age", "gender"],
            confidence_score=0.8,
            explanation="Bias detected in resume",
            recommendations=["Remove age", "Use neutral language"],
            pii_detected={"cpf": ["123.456.789-00"]},
            requires_human_review=True,
        )

        report = self.bias_service.create_bias_report(bias_result, "Sample resume text", "proc_123")

        assert "processing_id" in report
        assert report["processing_id"] == "proc_123"
        assert "timestamp" in report
        assert "bias_analysis" in report
        assert "detected_elements" in report
        assert "recommendations" in report
        assert "legal_basis" in report
        assert "compliance_status" in report
        assert report["compliance_status"] == "NON_COMPLIANT"

    def test_calculate_fairness_metrics_basic(self):
        """Test basic fairness metrics calculation."""
        scores_by_group = {"group_a": [0.8, 0.7, 0.9], "group_b": [0.6, 0.8, 0.7]}

        metrics = self.bias_service.calculate_fairness_metrics(scores_by_group)

        assert isinstance(metrics, FairnessMetrics)
        assert 0 <= metrics.demographic_parity <= 1
        assert 0 <= metrics.equal_opportunity <= 1
        assert 0 <= metrics.overall_fairness_score <= 1
        assert 0 <= metrics.disparate_impact_ratio <= 1
        assert metrics.sample_size == 6

    def test_calculate_fairness_metrics_insufficient_data(self):
        """Test fairness metrics with insufficient data."""
        scores_by_group = {}  # Empty data

        metrics = self.bias_service.calculate_fairness_metrics(scores_by_group)

        assert isinstance(metrics, FairnessMetrics)
        assert metrics.demographic_parity == 1.0  # Default values
        assert metrics.overall_fairness_score == 1.0
        assert metrics.sample_size == 0

    def test_calculate_fairness_metrics_perfect_fairness(self):
        """Test fairness metrics with perfectly fair distribution."""
        scores_by_group = {"group_a": [0.8, 0.8, 0.8], "group_b": [0.8, 0.8, 0.8]}

        metrics = self.bias_service.calculate_fairness_metrics(scores_by_group)

        assert metrics.demographic_parity == 1.0
        assert metrics.equal_opportunity == 1.0
        assert metrics.overall_fairness_score == 1.0
        assert metrics.disparate_impact_ratio == 1.0

    def test_protected_characteristics_brazilian_context(self):
        """Test protected characteristics with Brazilian context."""
        # Test Brazilian specific terms
        text = "Sou nordestino, moro na comunidade, estudou em escola pública"
        detected = self.bias_service.detect_protected_characteristics(text)

        assert "regional_origin" in detected or "social_background" in detected

    def test_pii_brazilian_formats(self):
        """Test PII detection with Brazilian formats."""
        text = """
        CPF: 123.456.789-00
        RG: 12.345.678-9
        CEP: 01234-567
        Telefone: (11) 98765-4321
        """

        pii = self.bias_service.detect_pii(text)

        assert "cpf" in pii
        assert "rg" in pii
        assert "phone" in pii

    def test_edge_case_empty_text(self):
        """Test bias analysis with empty text."""
        result = self.bias_service.analyze_text_bias("", "resume")

        assert isinstance(result, BiasDetectionResult)
        assert not result.has_bias
        assert result.severity == BiasSeverity.LOW
        assert len(result.detected_characteristics) == 0

    def test_edge_case_very_long_text(self):
        """Test bias analysis with very long text."""
        # Create a long text with some bias
        long_text = "Engenheiro " * 1000 + "35 anos de idade " + "masculino " * 500

        result = self.bias_service.analyze_text_bias(long_text, "resume")

        assert isinstance(result, BiasDetectionResult)
        # Should still detect bias even in long text
        assert (
            "age" in result.detected_characteristics or "gender" in result.detected_characteristics
        )

    def test_context_based_analysis(self):
        """Test bias analysis in different contexts."""
        text = "João Silva, 35 anos, engenheiro"

        resume_result = self.bias_service.analyze_text_bias(text, "resume")
        job_result = self.bias_service.analyze_text_bias(text, "job")
        general_result = self.bias_service.analyze_text_bias(text, "general")

        # All should detect bias
        assert resume_result.has_bias
        assert job_result.has_bias
        assert general_result.has_bias

    def test_unicode_and_special_characters(self):
        """Test bias analysis with Unicode and special characters."""
        text = "São Paulo, José García,ña, café, mês"

        # Should not crash with special characters
        result = self.bias_service.analyze_text_bias(text, "resume")
        assert isinstance(result, BiasDetectionResult)

    def test_mixed_language_text(self):
        """Test bias analysis with mixed Portuguese/English text."""
        text = "Software developer with 5 years of experience, 30 anos old"

        result = self.bias_service.analyze_text_bias(text, "resume")
        assert isinstance(result, BiasDetectionResult)
        # Should detect age in Portuguese
        assert "age" in result.detected_characteristics


if __name__ == "__main__":
    pytest.main([__file__])
