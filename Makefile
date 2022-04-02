build:
	docker build --target production -t awsomewebhook:lastet .
	docker build --target test -t awsomewebhook:test .


run: build
	docker rm -f awsomewebhook
	docker run -d --rm --name awsomewebhook -p 5000:5000 --env WEBHOOK_SECRET=${WEBHOOK_SECRET} \
	--env GITHUB_TOKEN=${GITHUB_TOKEN} awsomewebhook:lastet

test: 
	docker run --rm --name awsomewebhook-test awsomewebhook:test
	
clean:	 
	docker rm -f awsomewebhook

