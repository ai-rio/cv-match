"""
Comprehensive Bias Detection and Anti-Discrimination Service for CV-Match
Implements Brazilian legal compliance and fairness measures for AI scoring.

This service addresses critical security vulnerabilities identified in Phase 0.5:
- Prevents discrimination based on protected characteristics
- Ensures compliance with Brazilian law (Constitution, Lei das Cotas, LGPD)
- Implements PII detection and bias monitoring
- Provides transparency and human oversight mechanisms
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ..core.exceptions import ProviderError

logger = logging.getLogger(__name__)


class BiasSeverity(Enum):
    """Severity levels for bias detection."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BiasDetectionResult:
    """Result of bias analysis."""

    has_bias: bool
    severity: BiasSeverity
    detected_characteristics: list[str]
    confidence_score: float
    explanation: str
    recommendations: list[str]
    pii_detected: dict[str, list[str]]
    requires_human_review: bool


@dataclass
class FairnessMetrics:
    """Algorithmic fairness metrics."""

    demographic_parity: float
    equal_opportunity: float
    predictive_equality: float
    overall_fairness_score: float
    disparate_impact_ratio: float


class BiasDetectionService:
    """
    Comprehensive bias detection service for Brazilian market compliance.

    Protected characteristics under Brazilian law:
    - Age (idade)
    - Gender (gênero)
    - Race/ethnicity (raça/etnia)
    - Disability (deficiência)
    - Marital status (estado civil)
    - Religion (religião)
    - Political opinion (opinião política)
    - National origin (origem nacional)
    - Social background (background social)
    - Employment gaps (intervalos de emprego)
    """

    def __init__(self) -> None:
        """Initialize bias detection with Brazilian context."""
        self.protected_characteristics = self._initialize_protected_characteristics()
        self.pii_patterns = self._initialize_pii_patterns()
        self.bias_keywords = self._initialize_bias_keywords()
        self.fairness_thresholds = self._initialize_fairness_thresholds()

        logger.info("BiasDetectionService initialized with Brazilian legal compliance")

    def _initialize_protected_characteristics(self) -> dict[str, dict[str, Any]]:
        """Initialize protected characteristics for Brazilian context."""
        return {
            "age": {
                "pt_br": "idade",
                "patterns": [
                    r"\b\d{2}\s*(anos|anos de idade)\b",
                    r"\b(idade|anos)\s*:?\s*\d{2}\b",
                    r"\b(nascido em|nascida em)\s*\d{4}\b",
                    r"\b(\d{4})\b.*\b(nascimento|nasc)\b",
                ],
                "high_risk_keywords": ["jovem", "velho", "experiente demais", "muito jovem"],
                "legal_basis": "Constituição Federal Art. 3º, IV; Lei nº 9.029/95",
            },
            "gender": {
                "pt_br": "gênero",
                "patterns": [
                    r"\b(masculino|feminino|homem|mulher|ele|ela)\b",
                    r"\b(gênero|sexo)\s*:?\s*(masculino|feminino)\b",
                ],
                "high_risk_keywords": ["homem", "mulher", "masculino", "feminino"],
                "legal_basis": "Constituição Federal Art. 5º, I; Lei nº 9.029/95",
            },
            "race_ethnicity": {
                "pt_br": "raça/etnia",
                "patterns": [
                    r"\b(branco|preto|pardo|amarelo|indígena)\b",
                    r"\b(raça|etnia|cor)\s*:?\s*(\w+)\b",
                    r"\b(negro|afrodescendente|indígena)\b",
                ],
                "high_risk_keywords": ["cor", "raça", "etnia", "negro", "branco"],
                "legal_basis": "Constituição Federal Art. 3º, IV; Lei nº 12.288/2010 (Estatuto da Igualdade Racial)",
            },
            "disability": {
                "pt_br": "deficiência",
                "patterns": [
                    r"\b(deficiente|pcd|pne|deficiência)\b",
                    r"\b(necessidades especiais|acessibilidade)\b",
                    r"\b(cadeirante|surdo|cego|autista)\b",
                ],
                "high_risk_keywords": ["deficiente", "pcd", "deficiência"],
                "legal_basis": "Lei nº 7.853/89; Lei nº 8.112/90 (Cotas para PCD)",
            },
            "marital_status": {
                "pt_br": "estado civil",
                "patterns": [
                    r"\b(solteiro|casado|divorciado|viúvo|separado)\b",
                    r"\b(estado civil)\s*:?\s*(\w+)\b",
                ],
                "high_risk_keywords": ["casado", "solteiro", "filhos"],
                "legal_basis": "Constituição Federal Art. 5º, I",
            },
            "religion": {
                "pt_br": "religião",
                "patterns": [
                    r"\b(católico|protestante|evangélico|espírita|judeu|muçulmano)\b",
                    r"\b(religião|crença)\s*:?\s*(\w+)\b",
                ],
                "high_risk_keywords": ["religião", "igreja", "crença"],
                "legal_basis": "Constituição Federal Art. 5º, VI",
            },
            "employment_gaps": {
                "pt_br": "intervalos de emprego",
                "patterns": [
                    r"\b(parada|pausa|intervalo)\s*(de\s*)?\d{1,2}\s*(meses|anos)\b",
                    r"\b(desempregado|desocupado)\s*(desde\s*)?\d{4}\b",
                ],
                "high_risk_keywords": ["desempregado", "gap", "parou"],
                "legal_basis": "Lei nº 9.029/95 - não discriminação por situação empregatícia",
            },
            "regional_origin": {
                "pt_br": "origem regional",
                "patterns": [
                    r"\b(nordestino|sulista|norteiro|centro-oeste)\b",
                    r"\b(favela|comunidade|periferia)\b",
                ],
                "high_risk_keywords": ["favela", "periferia", "nordeste"],
                "legal_basis": "Constituição Federal Art. 3º, IV",
            },
            "social_background": {
                "pt_br": "background social",
                "patterns": [
                    r"\b(escola pública|escola particular)\b",
                    r"\b(bolsista|bolsa)\s*(de\s*)?(estudos)\b",
                ],
                "high_risk_keywords": ["escola pública", "pobre", "rico"],
                "legal_basis": "Constituição Federal Art. 3º, III",
            },
        }

    def _initialize_pii_patterns(self) -> dict[str, list[str]]:
        """Initialize PII detection patterns."""
        return {
            "cpf": [r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"],
            "rg": [r"\b\d{1,2}\.\d{3}\.\d{3}-\d{1}\b"],
            "phone": [r"\b\(\d{2}\)\s*\d{4,5}-\d{4}\b", r"\b\d{2}\s*\d{4,5}-\d{4}\b"],
            "email": [r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"],
            "address": [
                r"\b(rua|avenida|alameda|travessa)\s+[\w\s]+,\s*\d+[\w\s]*\b",
                r"\b(cep|código postal)\s*:?\s*\d{5}-\d{3}\b",
            ],
            "birth_date": [r"\b\d{2}/\d{2}/\d{4}\b", r"\b\d{4}-\d{2}-\d{2}\b"],
        }

    def _initialize_bias_keywords(self) -> dict[str, list[str]]:
        """Initialize keywords that indicate potential bias."""
        return {
            "age_bias": [
                "jovem demais",
                "muito velho",
                "muito jovem",
                "idade avançada",
                "aposentado",
                "pré-aposentadoria",
                "geração X",
                "geração Y",
                "millennial",
            ],
            "gender_bias": [
                "homem para",
                "mulher para",
                "masculino",
                "feminino",
                "sexo masculino",
                "sexo feminino",
                "força física",
                "delicadeza",
            ],
            "racial_bias": [
                "boa aparência",
                "boa aparência profissional",
                "sorriso bonito",
                "aparência cuidada",
                "boa aparência pessoal",
            ],
            "discriminatory": [
                "brasileiro",
                "não brasileiro",
                "nacionalidade",
                "natural de",
                "carga horária exclusiva",
                "disponibilidade para viagens frequentes",
            ],
        }

    def _initialize_fairness_thresholds(self) -> dict[str, float]:
        """Initialize fairness thresholds for bias detection."""
        return {
            "min_fairness_score": 0.8,
            "max_disparate_impact": 0.2,
            "min_demographic_parity": 0.7,
            "min_equal_opportunity": 0.7,
            "bias_confidence_threshold": 0.7,
        }

    def detect_pii(self, text: str) -> dict[str, list[str]]:
        """
        Detect Personally Identifiable Information in text.

        Args:
            text: Text to analyze for PII

        Returns:
            Dictionary with PII categories and detected values
        """
        detected_pii = {}

        for category, patterns in self.pii_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)

            if matches:
                detected_pii[category] = list(set(matches))  # Remove duplicates

        return detected_pii

    def detect_protected_characteristics(self, text: str) -> list[str]:
        """
        Detect protected characteristics in text.

        Args:
            text: Text to analyze for protected characteristics

        Returns:
            List of detected protected characteristics
        """
        detected = []
        text_lower = text.lower()

        for char_name, char_data in self.protected_characteristics.items():
            # Check pattern matches
            for pattern in char_data["patterns"]:
                if re.search(pattern, text_lower):
                    detected.append(char_name)
                    break

            # Check high-risk keywords
            for keyword in char_data["high_risk_keywords"]:
                if keyword.lower() in text_lower:
                    detected.append(char_name)
                    break

        return list(set(detected))

    def detect_bias_keywords(self, text: str) -> dict[str, list[str]]:
        """
        Detect potentially biased keywords in text.

        Args:
            text: Text to analyze for bias

        Returns:
            Dictionary with bias categories and detected keywords
        """
        detected_bias = {}
        text_lower = text.lower()

        for bias_category, keywords in self.bias_keywords.items():
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)

            if found_keywords:
                detected_bias[bias_category] = found_keywords

        return detected_bias

    def calculate_bias_risk_score(
        self,
        protected_chars: list[str],
        bias_keywords: dict[str, list[str]],
        pii_detected: dict[str, list[str]],
    ) -> tuple[float, BiasSeverity]:
        """
        Calculate overall bias risk score and severity.

        Args:
            protected_chars: List of detected protected characteristics
            bias_keywords: Dictionary of detected bias keywords
            pii_detected: Dictionary of detected PII

        Returns:
            Tuple of (risk_score, severity)
        """
        # Base risk from protected characteristics
        char_risk = len(protected_chars) * 0.3

        # Risk from bias keywords
        keyword_risk = sum(len(keywords) for keywords in bias_keywords.values()) * 0.2

        # Risk from PII detection
        pii_risk = len(pii_detected) * 0.1

        # Combined risk score
        total_risk = char_risk + keyword_risk + pii_risk
        normalized_score = min(total_risk / 2.0, 1.0)  # Normalize to 0-1

        # Determine severity
        if normalized_score >= 0.8:
            severity = BiasSeverity.CRITICAL
        elif normalized_score >= 0.6:
            severity = BiasSeverity.HIGH
        elif normalized_score >= 0.4:
            severity = BiasSeverity.MEDIUM
        else:
            severity = BiasSeverity.LOW

        return normalized_score, severity

    def analyze_text_bias(self, text: str, context: str = "resume") -> BiasDetectionResult:
        """
        Comprehensive bias analysis of text.

        Args:
            text: Text to analyze for bias
            context: Context of analysis (resume, job_description, prompt)

        Returns:
            BiasDetectionResult with comprehensive analysis
        """
        try:
            # Detect PII
            pii_detected = self.detect_pii(text)

            # Detect protected characteristics
            protected_chars = self.detect_protected_characteristics(text)

            # Detect bias keywords
            bias_keywords = self.detect_bias_keywords(text)

            # Calculate risk score
            risk_score, severity = self.calculate_bias_risk_score(
                protected_chars, bias_keywords, pii_detected
            )

            # Determine if human review is required
            requires_human_review = (
                severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]
                or len(protected_chars) > 2
                or len(pii_detected) > 0
            )

            # Generate explanation
            explanation = self._generate_bias_explanation(
                protected_chars, bias_keywords, pii_detected, severity
            )

            # Generate recommendations
            recommendations = self._generate_bias_recommendations(
                protected_chars, bias_keywords, pii_detected, context
            )

            return BiasDetectionResult(
                has_bias=risk_score > self.fairness_thresholds["bias_confidence_threshold"],
                severity=severity,
                detected_characteristics=protected_chars,
                confidence_score=risk_score,
                explanation=explanation,
                recommendations=recommendations,
                pii_detected=pii_detected,
                requires_human_review=requires_human_review,
            )

        except Exception as e:
            logger.error(f"Error analyzing text bias: {e}")
            raise ProviderError(f"Bias analysis failed: {str(e)}") from e

    def _generate_bias_explanation(
        self,
        protected_chars: list[str],
        bias_keywords: dict[str, list[str]],
        pii_detected: dict[str, list[str]],
        severity: BiasSeverity,
    ) -> str:
        """Generate explanation for bias detection."""
        explanation = f"Análise de viés detectou nível {severity.value} de risco."

        if protected_chars:
            char_names = [self.protected_characteristics[char]["pt_br"] for char in protected_chars]
            explanation += f" Características protegidas detectadas: {', '.join(char_names)}."

        if bias_keywords:
            all_keywords = []
            for keywords in bias_keywords.values():
                all_keywords.extend(keywords)
            explanation += (
                f" Palavras potencialmente discriminatórias: {', '.join(all_keywords[:5])}."
            )

        if pii_detected:
            pii_types = list(pii_detected.keys())
            explanation += f" Informações pessoais detectadas: {', '.join(pii_types)}."

        return explanation

    def _generate_bias_recommendations(
        self,
        protected_chars: list[str],
        bias_keywords: dict[str, list[str]],
        pii_detected: dict[str, list[str]],
        context: str,
    ) -> list[str]:
        """Generate recommendations for bias mitigation."""
        recommendations = []

        if pii_detected:
            recommendations.extend(
                [
                    "Remover todas as informações pessoais identificáveis (PII)",
                    "Anonimizar dados como CPF, RG, telefone e endereço",
                    "Evitar incluir datas de nascimento ou informações de contato",
                ]
            )

        if protected_chars:
            recommendations.extend(
                [
                    "Remover referências a características protegidas pela lei brasileira",
                    "Focar apenas em qualificações profissionais relevantes",
                    "Evitar menções a idade, gênero, raça ou outras características pessoais",
                ]
            )

        if bias_keywords:
            recommendations.extend(
                [
                    "Substituir termos potencialmente discriminatórios",
                    "Usar linguagem neutra e inclusiva",
                    "Focar em habilidades e competências mensuráveis",
                ]
            )

        if context == "prompt":
            recommendations.extend(
                [
                    "Adicionar regras explícitas anti-discriminação no prompt",
                    "Incluir instruções para avaliar apenas critérios relevantes à vaga",
                    "Implementar verificação de justiça algorítmica",
                ]
            )

        return recommendations

    def create_anti_discrimination_prompt(self, context: str = "scoring") -> str:
        """
        Create anti-discrimination instructions for AI prompts.

        Args:
            context: Context for the prompt (scoring, analysis, improvement)

        Returns:
            Anti-discrimination prompt text
        """
        base_rules = """
CRITICAL - REGRAS ANTI-DISCRIMINAÇÃO (Lei Brasileira):
- NÃO CONSIDERAR: idade, gênero, raça/etnia, religião, orientação sexual, deficiência
- NÃO PENALIZAR: intervalos de emprego, trajetórias não tradicionais, background social
- NÃO DISCRIMINAR: com base em nome, endereço, instituições de ensino, origem regional
- AVALIAR APENAS: habilidades relevantes, experiência profissional, qualificações para a vaga
- GARANTIR: tratamento justo independente de características protegidas
- FORNECER: razoamento transparente para todas as decisões de pontuação

BASE LEGAL:
- Constituição Federal Art. 3º, IV e Art. 5º, I
- Lei nº 9.029/95 - Proibição de discriminação
- Lei nº 12.288/2010 - Estatuto da Igualdade Racial
- Lei nº 7.853/89 - Pessoas com deficiência
- LGPD - Transparência em decisões automatizadas
"""

        context_specific = {
            "scoring": """
ESPECÍFICO PARA PONTUAÇÃO:
1. Avaliar apenas competências técnicas e experienciais relevantes
2. Ignorar completamente informações pessoais e características protegidas
3. Basear pontuação estritamente nos requisitos da vaga
4. Documentar critérios objetivos para cada pontuação atribuída
5. Sinalizar qualquer característica protegida detectada no currículo
""",
            "analysis": """
ESPECÍFICO PARA ANÁLISE:
1. Identificar e ignorar informações não relevantes para a vaga
2. Focar em habilidades mensuráveis e resultados profissionais
3. Detectar e reportar qualquer característica protegida encontrada
4. Fornecer análise baseada apenas em critérios profissionais
5. Garantir equidade na avaliação de diferentes perfis
""",
            "improvement": """
ESPECÍFICO PARA MELHORIA:
1. Melhorar apenas aspectos profissionais relevantes para a vaga
2. Remover informações pessoais e características protegidas
3. Destacar competências e experiências alinhadas à vaga
4. Usar linguagem inclusiva e neutra
5. Manter autenticidade profissional do candidato
""",
        }

        return base_rules + context_specific.get(context, "")

    def calculate_fairness_metrics(
        self, scores_by_group: dict[str, list[float]]
    ) -> FairnessMetrics:
        """
        Calculate algorithmic fairness metrics.

        Args:
            scores_by_group: Dictionary mapping groups to their scores

        Returns:
            FairnessMetrics object with calculated metrics
        """
        if not scores_by_group or len(scores_by_group) < 2:
            return FairnessMetrics(0.0, 0.0, 0.0, 0.0, 0.0)

        # Calculate demographic parity (difference in positive rates)
        group_averages = [sum(scores) / len(scores) for scores in scores_by_group.values()]
        max_avg = max(group_averages)
        min_avg = min(group_averages)
        demographic_parity = 1.0 - abs(max_avg - min_avg)

        # Calculate disparate impact ratio
        if min_avg > 0:
            disparate_impact = min_avg / max_avg
        else:
            disparate_impact = 0.0

        # Simplified equal opportunity and predictive equality (placeholder)
        # In practice, these would require ground truth labels
        equal_opportunity = demographic_parity  # Simplified
        predictive_equality = demographic_parity  # Simplified

        # Overall fairness score
        overall_fairness = (
            demographic_parity
            + equal_opportunity
            + predictive_equality
            + (1 - abs(disparate_impact - 1))
        ) / 4

        return FairnessMetrics(
            demographic_parity=demographic_parity,
            equal_opportunity=equal_opportunity,
            predictive_equality=predictive_equality,
            overall_fairness_score=overall_fairness,
            disparate_impact_ratio=disparate_impact,
        )

    def should_block_processing(self, bias_result: BiasDetectionResult) -> bool:
        """
        Determine if processing should be blocked due to bias risk.

        Args:
            bias_result: Result of bias analysis

        Returns:
            True if processing should be blocked
        """
        return (
            bias_result.severity == BiasSeverity.CRITICAL
            or (bias_result.severity == BiasSeverity.HIGH and len(bias_result.pii_detected) > 0)
            or bias_result.confidence_score > 0.9
        )

    def create_bias_report(
        self, bias_result: BiasDetectionResult, text_sample: str, processing_id: str
    ) -> dict[str, Any]:
        """
        Create comprehensive bias report for auditing.

        Args:
            bias_result: Result of bias analysis
            text_sample: Sample of analyzed text (sanitized)
            processing_id: Unique identifier for processing

        Returns:
            Comprehensive bias report
        """
        return {
            "processing_id": processing_id,
            "timestamp": datetime.utcnow().isoformat(),
            "bias_analysis": {
                "has_bias": bias_result.has_bias,
                "severity": bias_result.severity.value,
                "confidence_score": bias_result.confidence_score,
                "requires_human_review": bias_result.requires_human_review,
            },
            "detected_elements": {
                "protected_characteristics": bias_result.detected_characteristics,
                "pii_detected": bias_result.pii_detected,
                "risk_factors_count": len(bias_result.detected_characteristics)
                + len(bias_result.pii_detected),
            },
            "recommendations": bias_result.recommendations,
            "explanation": bias_result.explanation,
            "legal_basis": {
                char: self.protected_characteristics[char]["legal_basis"]
                for char in bias_result.detected_characteristics
                if char in self.protected_characteristics
            },
            "sample_text": text_sample[:500] + "..." if len(text_sample) > 500 else text_sample,
            "compliance_status": "COMPLIANT" if not bias_result.has_bias else "NON_COMPLIANT",
        }


# Singleton instance for application-wide use
bias_detection_service = BiasDetectionService()
