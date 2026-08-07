"""Multi-dimensional Data Quality Scoring Engine."""

from typing import List

from src.quality.models.quality_result import ProfileResult, QualityScore, RuleResult


class QualityScorer:
    """Engine computing weighted quality scores across completeness, uniqueness, and validity."""

    @staticmethod
    def calculate_score(profile: ProfileResult, rule_results: List[RuleResult]) -> QualityScore:
        """Calculate weighted Data Quality Score.

        Dimensions:
        - Completeness (35% weight): Average non-null ratio across all columns.
        - Uniqueness (25% weight): Ratio of unique records (100 - duplicate_percentage).
        - Validity (40% weight): Pass ratio of evaluation rules.

        Args:
            profile: Statistical profile result.
            rule_results: List of evaluated rule results.

        Returns:
            QualityScore: Computed multi-dimensional quality score model.
        """
        # Completeness Calculation
        if profile and profile.column_profiles:
            avg_null_pct = sum(p.null_percentage for p in profile.column_profiles.values()) / len(
                profile.column_profiles
            )
            completeness = max(0.0, 100.0 - avg_null_pct)
        else:
            completeness = 100.0

        # Uniqueness Calculation
        if profile:
            uniqueness = max(0.0, 100.0 - profile.duplicate_percentage)
        else:
            uniqueness = 100.0

        # Validity Calculation
        if rule_results:
            passed_rules = sum(1 for r in rule_results if r.passed)
            validity = (passed_rules / len(rule_results)) * 100.0
        else:
            validity = 100.0

        # Overall Weighted Score: 35% Completeness + 25% Uniqueness + 40% Validity
        overall_score = round((0.35 * completeness) + (0.25 * uniqueness) + (0.40 * validity), 2)

        if overall_score >= 90.0:
            grade = "A"
        elif overall_score >= 80.0:
            grade = "B"
        elif overall_score >= 70.0:
            grade = "C"
        else:
            grade = "F"

        return QualityScore(
            completeness_score=round(completeness, 2),
            uniqueness_score=round(uniqueness, 2),
            validity_score=round(validity, 2),
            overall_quality_score=overall_score,
            quality_grade=grade,
        )
