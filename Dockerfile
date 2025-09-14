FROM alpine:3.22.1

COPY . /usr/local/share/fsprot

RUN apk update && apk add bash shadow \
    && addgroup -g 1000 john \
    && adduser -u 1000 -G john -h /home/john -s /bin/bash -D john \
    && echo "john:pwd" | chpasswd \
    && addgroup -g 1001 doe \
    && adduser -u 1001 -G doe -h /home/doe -s /bin/bash -D doe \
    && echo "doe:pwd" | chpasswd \
    && chmod u+s /bin/su

USER john
WORKDIR /home/john

ENTRYPOINT ["/bin/bash"]
