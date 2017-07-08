// WRITE SERVER
// READ FORM REDIS CHANNEL
// UPDATE UI IN REAL TIME
var argv = require('minimist')(process.argv.slice(2));
var redis_host = argv['redis_host'];
var redis_port = argv['redis_port'];
var redis_channel = argv['redis_channel'];

var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io')(server);

var redis = require('redis');
console.log('created redis client');
var redisClient = redis.createClient(redis_port, redis_host);
redisClient.subscribe(redis_channel);
console.log('subscribe to redis channel %s', redis_channel);

// when new meaasge arrives, invoke function
redisClient.on('message', function (channel, message) {
	console.log(channel,redis_channel)
	if (channel == redis_channel)  {
		console.log('message received %s', message)
		io.sockets.emit('data', message)
	}
});

app.use('/', express.static(__dirname + '/public'));
app.use('/jquery', express.static(__dirname + '/node_modules/jquery/dist'));
app.use('/bootstrap', express.static(__dirname + '/node_modules/bootstrap/dist'));
app.use('/d3', express.static(__dirname + '/node_modules/d3/'));
app.use('/nvd3', express.static(__dirname + '/node_modules/nvd3/build/'));

server.listen(3000, function() {
	console.log('server start at port 3000.')
})

// - setup shutdown hooks
var shutdown_hook = function () {
    console.log('Quitting redis client');
    redisclient.quit();
    console.log('Shutting down app');
    process.exit();
};

process.on('SIGTERM', shutdown_hook);
process.on('SIGINT', shutdown_hook);
process.on('exit', shutdown_hook);