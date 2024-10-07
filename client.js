const net = require('net');
const crypto = require('crypto');

const client = new net.Socket();
client.connect(8080, '127.0.0.1', function() {
	console.log('Connected');
	const data = {
        "name": "Daniel",
        "last_name": "Mercado"
    }

	client.write(`add:${crypto.randomUUID()}:${JSON.stringify(data)}`);
});

client.on('data', function(data) {
	console.log('Received: ' + data);
	client.destroy();
});

client.on('close', function() {
	console.log('Connection closed');
});