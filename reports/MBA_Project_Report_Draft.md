# MBA Business Analytics Project Report – Working Draft

## 1. Introduction
This project investigates machine learning for next-month credit-card default-risk estimation. It uses the UCI Default of Credit Card Clients dataset and develops a preliminary decision-support prototype.

## 2. Business Problem
Credit-card issuers manage repayment risk across large customer portfolios. An early-warning model may help prioritise accounts for qualified review and customer engagement. The prototype is intended to support, not replace, human judgement.

## 3. Dataset Description
The uploaded workbook contains 30,000 observations and 25 columns: ID, 23 predictors and `default payment next month`. There are 23,364 non-defaults (77.88%) and 6,636 defaults (22.12%). The source population is historical Taiwanese credit-card customers from 2005.

## 4. Data Preparation
The actual header row was spreadsheet row 2; row 1 contained generic X1–X23/Y labels. Inspection found zero missing cells, zero exact duplicate rows and 30,000 unique IDs. ID was excluded. SEX, EDUCATION and MARRIAGE were treated as nominal categorical codes and one-hot encoded; the remaining features were numeric in this first experiment. Unusual category codes remain a review item for the group.

## 5. Exploratory Data Analysis
The overall default rate is 22.12%. Observed default rates differ by latest repayment-status code (PAY_0): code 0 is 12.81% (n=14,737), code 1 is 33.95% (n=3,688) and code 2 is 69.14% (n=2,667). Rare codes have small group sizes and should be interpreted carefully.

The observed default rate by credit-limit band ranges from 31.79% for <= NT$50,000 to 13.26% for > NT$300,000. This is an association in this sample, not evidence that changing a credit limit would cause default risk to change.

## 6. Machine Learning Methodology
The task is supervised binary classification. A stratified 80/20 development/test split was used; within the development set, a 90/10 training/validation split was used. Preprocessing was placed in scikit-learn pipelines to avoid fitting transformations on validation or test data. Candidate algorithms were Logistic Regression, Decision Tree and Random Forest. Candidate selection used validation default-class F1 with ROC-AUC as tie-break. The selected candidate was refit on development data and evaluated once on the held-out test set.

## 7. Model Evaluation
The selected preliminary model was Random Forest. At threshold 0.50, held-out test results were: accuracy 79.32%, default-class precision 53.17%, default-class recall 54.41%, F1 0.538, ROC-AUC 0.774, average precision 0.552 and Brier score 0.156. Confusion matrix counts were TN=4,037, FP=636, FN=605, TP=722.

The 605 false negatives are missed defaults in this test sample; the 636 false positives are non-defaulters flagged as defaults. Management must define the relative costs of these errors before choosing a threshold.

## 8. Business Interpretation
Repayment history contains useful predictive information, but the model misses a substantial share of actual defaults at the 0.50 threshold. The system may be considered a prioritisation aid for human review and customer outreach after further validation. It should not automatically make credit or collection decisions.

## 9. Streamlit Application
The starter application contains three pages: Business Overview, Data Insights and Prediction. Prediction remains disabled in the published repository until the trusted model artifact has been generated and added. The local project archive contains the saved model artifact.

## 10. GitHub Repository
Repository: https://github.com/Vineet-singh-01/credit-card-default-prediction. Source, notebooks, model metadata, audit and reports are published to the public main branch.

## 11. Deployment
A GitHub Actions workflow is provided to download the official UCI workbook and reproduce the model artifact. The group must run the workflow, verify the generated artifact, and then deploy through Streamlit Community Cloud. Public deployment is not yet completed or verified.

## 12. Limitations
- Dataset is from Taiwan in 2005 and does not represent current Indian credit-card customers.
- No recent external validation has been performed.
- Model score calibration has not been completed.
- Threshold 0.50 is not a business decision threshold.
- Demographic variables are present; fairness assessment and a model excluding demographic attributes are required.
- Observed relationships are not causal.

## 13. Recommendations and Next Work
1. Review education and marital-status code definitions and document treatment of unusual codes.
2. Compare a model excluding demographic attributes.
3. Calibrate the final model and inspect calibration curves.
4. Choose a threshold using a transparent cost matrix for false negatives and false positives.
5. Conduct robust cross-validation or temporal/external validation.
6. Validate user input constraints and perform application security review.

## 14. Conclusion
The dataset supports a meaningful credit-risk analytics exercise. The preliminary Random Forest candidate demonstrates predictive signal beyond a majority-class baseline. Further model, fairness, calibration and deployment checks remain necessary before operational use.

## Group work allocation
See `reports/group_work_plan.md`. Each member must understand and defend the complete project.

## Source
Yeh, I-C. (2009). Default of Credit Card Clients [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H. CC BY 4.0.
