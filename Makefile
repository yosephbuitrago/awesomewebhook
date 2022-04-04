build:
	docker build --target production -t awesomewebhook:lastet .
	docker build --target test -t awesomewebhook:test .

docker-stop:
	docker rm -f awesomewebhook

run: build docker-stop
	docker run -d --rm --name awesomewebhook -p 5000:5000 --env WEBHOOK_SECRET=${WEBHOOK_SECRET} \
	--env GITHUB_TOKEN=${GITHUB_TOKEN} awesomewebhook:lastet

run-debug: docker-stop
	docker run --rm --name awesomewebhook -p 5000:5000 --env WEBHOOK_SECRET=${WEBHOOK_SECRET} \
	--env GITHUB_TOKEN=${GITHUB_TOKEN} awesomewebhook:lastet

test: build
	docker run --rm --name awesomewebhook-test awesomewebhook:test

clean:
	docker rm -f awesomewebhook
