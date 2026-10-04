# Full direct diagnostic returns

Canonical published Base; unchanged diet values and unknowns. Constructor admission only; no invented coefficients.

## GE

```json
{
  "status": "NOT_RUN",
  "reason": "Constructor exception",
  "exception": {
    "type": "ValueError",
    "message": "5 consumer group(s) have a diet composition (including diet_import) that does not sum to 1 (tol=0.001): 23 (Groupers ad)=2.2006, 18 (Catfish ad)=0.9974, 16 (Seabreams ad)=0.9984, 9 (Sardinelles)=1.0016, 2 (Coastal birds)=0.9803.",
    "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\run_direct.py\", line 106, in main\n    warnings.simplefilter('always');c=PPRCalculator.from_modeldata(m,**settings)\n                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\engine\\PPRCalculator.py\", line 218, in from_modeldata\n    instance._DC = ModelData.validate_DC(instance._DC, instance._groups_df, tol=DC_tol, normalize=normalize_DC)\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\engine\\ModelData.py\", line 656, in validate_DC\n    raise ValueError(\nValueError: 5 consumer group(s) have a diet composition (including diet_import) that does not sum to 1 (tol=0.001): 23 (Groupers ad)=2.2006, 18 (Catfish ad)=0.9974, 16 (Seabreams ad)=0.9984, 9 (Sardinelles)=1.0016, 2 (Coastal birds)=0.9803.\n"
  }
}
```

## TE

```json
{
  "status": "NOT_RUN",
  "reason": "Constructor exception",
  "exception": {
    "type": "ValueError",
    "message": "5 consumer group(s) have a diet composition (including diet_import) that does not sum to 1 (tol=0.001): 23 (Groupers ad)=2.2006, 18 (Catfish ad)=0.9974, 16 (Seabreams ad)=0.9984, 9 (Sardinelles)=1.0016, 2 (Coastal birds)=0.9803.",
    "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\run_direct.py\", line 106, in main\n    warnings.simplefilter('always');c=PPRCalculator.from_modeldata(m,**settings)\n                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\engine\\PPRCalculator.py\", line 218, in from_modeldata\n    instance._DC = ModelData.validate_DC(instance._DC, instance._groups_df, tol=DC_tol, normalize=normalize_DC)\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\engine\\ModelData.py\", line 656, in validate_DC\n    raise ValueError(\nValueError: 5 consumer group(s) have a diet composition (including diet_import) that does not sum to 1 (tol=0.001): 23 (Groupers ad)=2.2006, 18 (Catfish ad)=0.9974, 16 (Seabreams ad)=0.9984, 9 (Sardinelles)=1.0016, 2 (Coastal birds)=0.9803.\n"
  }
}
```

## With Egestion

```json
{
  "status": "NOT_RUN",
  "reason": "Constructor exception",
  "exception": {
    "type": "ValueError",
    "message": "5 consumer group(s) have a diet composition (including diet_import) that does not sum to 1 (tol=0.001): 23 (Groupers ad)=2.2006, 18 (Catfish ad)=0.9974, 16 (Seabreams ad)=0.9984, 9 (Sardinelles)=1.0016, 2 (Coastal birds)=0.9803.",
    "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\run_direct.py\", line 106, in main\n    warnings.simplefilter('always');c=PPRCalculator.from_modeldata(m,**settings)\n                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\engine\\PPRCalculator.py\", line 218, in from_modeldata\n    instance._DC = ModelData.validate_DC(instance._DC, instance._groups_df, tol=DC_tol, normalize=normalize_DC)\n                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\idoca\\Desktop\\אישי\\אקדמיה\\תואר שני\\מחקר\\BTN\\GlobalPPREstimation\\regions\\LME_027\\validation_reports\\BancArguin_20261003\\runtime\\engine\\ModelData.py\", line 656, in validate_DC\n    raise ValueError(\nValueError: 5 consumer group(s) have a diet composition (including diet_import) that does not sum to 1 (tol=0.001): 23 (Groupers ad)=2.2006, 18 (Catfish ad)=0.9974, 16 (Seabreams ad)=0.9984, 9 (Sardinelles)=1.0016, 2 (Coastal birds)=0.9803.\n"
  }
}
```