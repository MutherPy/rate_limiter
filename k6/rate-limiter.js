import http from 'k6/http';

const ips = ['192.0.2.1', '192.0.2.2', '192.0.2.3', '192.0.3.1', '192.0.3.2', '192.0.3.3'];

http.setResponseCallback(http.expectedStatuses(200, 429));

export const options = {
  scenarios: {
    rate_limiter: {
      executor: 'constant-arrival-rate',
      rate: 100,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 20,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_reqs{status:429}': ['count>0'],
  },
};

export default function () {
  const ip = ips[Math.floor(Math.random() * ips.length)];

  http.get(__ENV.TARGET_URL, {
    headers: { 'X-Forwarded-For': ip },
    redirects: 0,
  });
}
