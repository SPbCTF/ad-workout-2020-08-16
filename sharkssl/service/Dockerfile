FROM node:14-slim AS builder

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn

COPY . .

RUN yarn build

FROM node:14-slim

WORKDIR /app

COPY package.json yarn.lock ./

COPY --from=builder /app/dist .

RUN yarn install --prod

EXPOSE 3000

COPY healthcheck.js .

HEALTHCHECK --interval=5s CMD node ./healthcheck.js

CMD ["node", "src/index.js"]