import { getWebInstrumentations, initializeFaro } from "@grafana/faro-web-sdk";
import { TracingInstrumentation } from "@grafana/faro-web-tracing";

const url = import.meta.env.PUBLIC_GRAFANA_FARO_URL;
const apiKey = import.meta.env.PUBLIC_GRAFANA_FARO_API_KEY;
const environment = import.meta.env.PUBLIC_GRAFANA_FARO_ENVIRONMENT ?? "development";

if (url) {
  initializeFaro({
    url,
    ...(apiKey ? { apiKey } : {}),
    app: {
      name: "Dice and Paint Dev",
      version: "1.0.0",
      environment,
    },
    instrumentations: [
      ...getWebInstrumentations(),
      new TracingInstrumentation(),
    ],
  });
}
