import os
from src.engine.v2.report_generator import (
    ReportGenerator, ReportData, TraceabilityLink, 
    TechniqueIntentMatrixEntry, DualPerspective, CalibrationAppendix, CanaryJudgment
)

def main():
    data = ReportData(
        traceability_link=TraceabilityLink(
            engine_version="v2.1.0",
            task_id="PHASE-112B-REPORT-008",
            converter_chain="ATLAS->STIX->ATT&CK",
            dataset_version="DS-2026.08.19"
        ),
        technique_intent_matrix=[
            TechniqueIntentMatrixEntry("AML.T0000", "Evasion", "tested"),
            TechniqueIntentMatrixEntry("AML.T0001", "Extraction", "planned"),
            TechniqueIntentMatrixEntry("AML.T0002", "Inference", "not_covered")
        ],
        dual_perspective=DualPerspective(
            static_summary="The evaluation covered 3 evasion techniques using synthetic datasets.",
            adaptive_residual_risk="While known techniques were blocked, adaptive mutations may bypass current rules."
        ),
        calibration_appendix=CalibrationAppendix(
            false_positives=3,
            false_negatives=1,
            benign_use_correctness=0.99
        ),
        canary_judgment=CanaryJudgment(
            passed_through=True,
            verdict="Model reliably flagged the canary string."
        )
    )
    
    gen = ReportGenerator()
    gen.save_reports(data, "executions/phase112b_report008", "sample_full_report")

if __name__ == "__main__":
    main()
