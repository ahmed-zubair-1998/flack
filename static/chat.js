document.addEventListener('DOMContentLoaded', () => {

	// Connect to websocket
	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
	var room = window.location.pathname.split('/')[2];
	
	socket.on('connect', () => {
		
		socket.emit('on connect');
		document.getElementById('send').onclick = function() {
			message = document.getElementById('message').value;
			socket.emit('send message', {'message': message, 'room': room });
			document.getElementById('message').value = '';
		}
	});
	
	socket.emit('join', {'room': room});

	socket.on('message recieved', data => {
		const li = document.createElement('li');
		li.innerHTML = data.message;
		document.getElementById('messages').appendChild(li);
	});
	
	document.getElementById('leave').onclick = function() {
		socket.emit('leave', {'room': room});
		redirect
	}
});