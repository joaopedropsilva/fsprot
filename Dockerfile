FROM alpine:3.22.1

COPY . /tmp/fsprot

RUN apk update && apk add bash shadow python3 build-base libcap \
    && addgroup -g 1000 john \
    && adduser -u 1000 -G john -h /home/john -s /bin/bash -D john \
    && echo "john:pwd" | chpasswd \
    && addgroup -g 1001 doe \
    && adduser -u 1001 -G doe -h /home/doe -s /bin/bash -D doe \
    && echo "doe:pwd" | chpasswd \
    && chmod u+s /bin/su \
    && /tmp/fsprot/setup.sh

ENTRYPOINT ["/bin/bash"]
