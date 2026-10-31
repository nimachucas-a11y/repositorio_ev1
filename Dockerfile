FROM golang:1.26.1 AS build
WORKDIR /app
COPY src/ .
RUN CGO_ENABLED=0 go build -o /out/microservicio .

FROM scratch
COPY --from=build /out/microservicio /microservicio
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/microservicio"]
