# AWS Connect Vanify

Serverless powered AWS Connect sample hotline that converts the provided phone number into vanity numbers.

## Preview

This sample app is **live**.
You can view the most recent five calls [here](https://vanify.bradenmars.me).

You can try it out yourself by dialing: **+1 214-256-5172**


## Getting Started

* Create an AWS Connect instance.

* Setup your backend `.env` file:

> Alternatively, pass `INSTANCE_ID=abc ...` when deploying via serverless.

```bash
# backend/.env
INSTANCE_ID=myinstanceid
```

* Install root serverless dependencies.
```bash
# @ repo root
$ yarn install
```

* Deploy!
```bash
$ yarn deploy:backend  # a.k.a: sls deploy (from ./backend)
```

## Notes

### Production

This sample app would require (at least) the following for a production instance:
* Api Gateway / Lambda Authorization.
* Replication across different regions.
* Higher test coverage.
