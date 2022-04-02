build:
	docker build --target production -t awsomewebhook:lastet .
	docker build --target test -t awsomewebhook:test .

run: 
	docker run -d --rm --name awsomewebhook -p 5000:5000 awsomewebhook:lastet

test: 
	docker run --rm --name awsomewebhook-test awsomewebhook:test
	
clean:	 
	docker rm -f awsomewebhook

