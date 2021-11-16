# tap-dynamics

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap pulls raw data from Dynamics 365 CRM OData API.


## Example Meltano.yml config

```
- name: tap-dynamics
  namespace: tap_dynamics
  pip_url: git+ssh://git@github.com/quickbi/tap-dynamics.git
  settings:
    - name: client_id
    - name: client_secret
    - name: tenant_id
    - name: base_url
    - name: api_url
  config:
    start_date: "2000-01-01"
    tables:
      - accounts
      - leads
      - opportunities
```

Environment variables are also needed:
```
export TAP_DYNAMICS_CLIENT_ID="<client_id>"
export TAP_DYNAMICS_CLIENT_SECRET="<client_secret>"
export TAP_DYNAMICS_TENANT_ID="<tenant_id>"
export TAP_DYNAMICS_API_URL="https://<something>.dynamics.com/api/data/v9.2/"
export TAP_DYNAMICS_BASE_URL="https://<something-else>.dynamics.com/"
```
