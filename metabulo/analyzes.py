from scipy.stats import wilcoxon
import pandas as pd
from typing import Dict, Any, Optional


def wilcoxon_test(measurements: pd.DataFrame, zero_method: Optional[str] = None, alternative: Optional[str] = None) -> Dict[str, Any]:
    if zero_method is None:
        zero_method = 'wilcox'
    if alternative is None:
        alternative = 'two-sided'
    # TODO 
    return {
        'va': 5,
    }
