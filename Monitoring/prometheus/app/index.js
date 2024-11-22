var express = require('express');
var promClient = require('prom-client');
const register = promClient.register;

var app = express();

const counter = new promClient.Counter({
	name: 'aula_request_total',
	help: 'Contador de requests',
	labelNames: ['statusCode']
});

const gauge = new promClient.Gauge({
	name: 'aula_free_bytes',
	help: 'Exemplo de gauge'
});

const histogram = new promClient.Histogram({
	name: 'aula_request_time_seconds',
	help: 'Tempo de resposta da API',
	buckets: [0.1, 0.2, 0.3, 0.4, 0.5]
});

const summary = new promClient.Summary({
	name: 'aula_summary_request_time_seconds',
	help: 'Tempo de resposta da API',
	percentiles: [0.5, 0.9, 0.99]
});

app.get('/', function (req, res) {
	counter.labels('200').inc();
	counter.labels('300').inc();
	gauge.set(100 * Math.random());
	const tempo = Math.random();
	histogram.observe(tempo);
	summary.observe(tempo);

	res.send('Hello World!');
});

app.get('/metrics', async function (req, res) {
	res.set('Content-Type', register.contentType);
	res.end(await register.metrics());
})

app.listen(3000);