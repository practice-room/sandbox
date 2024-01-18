# Regenerating Test Data
This document is created to guide us in case we need to regenerate the test data.
It also captures traceability between tests and how the test data is generated.

Run everything from the root directory of the repository

## HC-01, HC-02, HC-03, HC-05, HC-07, HC-08, HC-12, HC-14, HC-16

```bash
for i in community redhat partner; do
    chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-0.17.0.tgz?raw=true --set profile.vendorType=${i} | tee tests/data/common/${i}/report.yaml; 
done

```

##2 HC-04

```bash
for i in community redhat partner; do
    chart-verifier verify tests/data/hc-e2e-vault-0.17.0.tgz --set profile.vendorType=${i} | tee tests/data/HC-04/${i}/report.yaml; 
done
```

### HC-06

```bash
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-0.17.0.tgz?raw=true --web-catalog-only | tee tests/data/HC-06/partner/report.yaml
```

### HC-09

```bash
for i in community redhat partner; do
    chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-0.17.0.tgz?raw=true --set profile.vendorType=${i} -o json | jq | tee tests/data/HC-09/${i}/report.json; 
done
```

### HC-11

```bash
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-0.17.0.tgz?raw=true -x helm-lint | tee tests/data/HC-11/partner/report.yaml
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-0.17.0.tgz?raw=true -x not-contains-crds | tee tests/data/HC-11/partner_not_contain_crds/report.yaml
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-0.17.0.tgz?raw=true --set profile.vendorType=community -x helm-lint | tee tests/data/HC-11/community/report.yaml
```

### HC-17

```bash
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-psql-svc-0.1.10-1.tgz?raw=true | tee tests/data/HC-17/dash-in-version/partner/report.yaml
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-psql-svc-0.1.10-1.tgz?raw=true --set profile.vendorType=redhat | tee tests/data/HC-17/dash-in-version/redhat/report.yaml
```

### HC-18

```bash
for i in community redhat partner; do
    chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-next-0.18.0.tgz?raw=true --set profile.vendorType=${i} | tee tests/data/HC-18/${i}/report.json; 
done
```

### HC-19

!! Manual steps here

```bash
# Modify the testedOpenShiftVersion value in report.yaml
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-0.17.0.tgz?raw=true | tee tests/data/HC-19/report_sha_good/report.yaml
# Modify the reportDigest value itself in report.yaml
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/hc-e2e-vault-0.17.0.tgz?raw=true | tee tests/data/HC-19/report_sha_bad/report.yaml

```

### HC-10

TODO: Automate this process using a container to generate throwaway keys.

Untar the signed chart for modification, and move existing chart and provenance out of the way.
```bash
tar xzvf tests/data/HC-10/signed_chart/hc-e2e-signed-vault-0.17.0.tgz -C tests/data/HC-10/signed_chart/
mv tests/data/HC-10/signed_chart/hc-e2e-signed-vault-0.17.0.tgz{,.bak}
mv tests/data/HC-10/signed_chart/hc-e2e-signed-vault-0.17.0.tgz.prov{,.bak}
```

Make modifications, then re-sign the chart.

```bash
cd tests/data/HC-10/signed_chart/
helm package --sign --key 'hc-e2e-ci-throwaway' --keyring $HOME/.gnupg/secring.gpg hc-e2e-signed-vault
 # Response E.g.:
 # Password for key "hc-e2e-ci-throwaway <throwaway@example.com>" >  
 # Successfully packaged chart and saved it to: <path-to-chart>
```

Verify (`helm verify`) the resulting chart tar and .prov file should be under tests/data/HC-10/signed_chart

Also generate your public key and copy it into the same tests/data/HC-10/signed_chart directory using below cmd:
```bash
gpg --export --armour hc-e2e-ci-throwaway > public_key_good.asc
```

Then generate reports

```bash
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/HC-10/signed_chart/hc-e2e-signed-vault-0.17.0.tgz?raw=true -k tests/data/HC-10/signed_chart/public_key_good.asc | tee tests/data/HC-10/signed_chart/report/partner/report.yaml
chart-verifier verify https://github.com/openshift-helm-charts/development/blob/main/tests/data/HC-10/signed_chart/hc-e2e-signed-vault-0.17.0.tgz?raw=true -k tests/data/HC-10/signed_chart/public_key_good.asc --set profile.vendorType=redhat | tee tests/data/HC-10/signed_chart/report/redhat/report.yaml
```