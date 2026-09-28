# LME_050 direct SPPR diagnostics

Only the complete direct `diagnose_sppr()` returns for GE, TE and With Egestion are represented. Footprint quantities belong to the loaded coastal-Kyoto models; they are not regional annual PPR.

| Year | Configuration | Status | b | Living spectral radius | Balance relative gap | PPR all | PPR inner | PPR PP only |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 1985 | GE | WARN | 0.01918493651 | 0.1060445413 | 2.032865299e-16 | 433.7914973 | 362.4739531 | 360.0268911 |
| 1985 | TE | WARN | 0 | 0.2441561799 | 2.032865299e-16 | 1159.386035 | 999.9641435 | 958.5378519 |
| 1985 | With Egestion | WARN | 0.01945577343 | 0.08483563303 | 2.032865299e-16 | 282.5250026 | 226.8486321 | 224.8925905 |
| 2013 | GE | WARN | 0.03129442747 | 0.1060445413 | 1.232836714e-16 | 83.09784055 | 67.8619438 | 65.10526629 |
| 2013 | TE | WARN | 0 | 0.2461420247 | 1.232836714e-16 | 969.7225065 | 927.587962 | 902.1084941 |
| 2013 | With Egestion | WARN | 0.03179448901 | 0.08483563303 | 2.465673427e-16 | 49.1481273 | 38.29651095 | 36.38765515 |

Complete readable returned fields:

- [1985: model_input, divergence, balance, footprint, config, warnings](../50_501985_Coastal_Kyoto_Inoue_(1985)/SPPR_DIAGNOSTICS.md)
- [2013: model_input, divergence, balance, footprint, config, warnings](../50_502013_Coastal_Kyoto_Inoue_(2013)/SPPR_DIAGNOSTICS.md)

[Complete full-precision method-return JSON](DIAGNOSE_SPPR_RESULTS.json). All six calls returned `WARN`; all report zero negative sources. EE=0 groups are #23 Ivory shell and #34 Brittle star in 1985, and #30 Tongue sole in 2013. The TE return warns that its recycling matrix is absent and b=0 by construction.
