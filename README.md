# Image finder

A image finder tool, that use SIFT to generate descriptor and use BFMATCHER or FLANN to match identical picture in the DB. 
Not merged to DB because....

## Tech Stack

**Client:** Next, TailwindCSS, ShadcnUI

**Server:** Node, Express, Flask

**CMS:** Payload CMS

**Message broker:** RabbitMQ

**User management/Role management:** Clerk, Payload(can be used but not in this project)

**DB:** MongoDB, PostgreSQL(Payload supports it in v3.0 but its in beta RN)

**Image processing:** Python, OpenCV



## Installation and run locally

### Install and run FE with npm

```bash
  git clone https://github.com/evoreign/image-finder-revised/tree/experimental
  cd image-finder-revised
  cd FE
  cd image-finder-fe
  npm Install
```
create new .env file with .env copy format
```bash
    npm run dev
```

### Install and run CMS

```bash
  git clone https://github.com/evoreign/image-finder-revised/tree/experimental
  cd image-finder-revised
  cd BE
  cd image-finder-cms
  npm Install
```
create new .env file with .env copy format
```bash
    npm run dev
```

### Install and run RabbitMQ

Run RabbitMQ service in your env

```bash
  git clone https://github.com/evoreign/image-finder-revised/tree/experimental
  cd image-finder-revised
  cd BE
  cd rabbitmq worker experiment
  python send.py
  python receive.py
```
## (Flask)API Reference

#### Get all items

```http
  POST 127.0.0.1:80/search
```

| Body | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `image` | `file` | **Required**. The image duh |

#### returns {UUID}.

#### Get item

```http
  GET /imagesearch/{UUID}
```

#### returns list of best matching image.



## Optimizations

In this method (SIFT and BFMatcher/FLANN) the only way is to downsize the DB, current performance is highly dependant on DB read and write speed on ideal condition at ~100 pic PNG image similarities result can be achive in ~10 seconds at current condition ~500 pic PNG takes forever (timedout from the DB when testing). Tried resizing the image is no use cause it destroys the result, the only way now is to do transfer learning from other model or do template matching(this is also a useless enddevour because scaling would be a major problem different resolution means different result)
