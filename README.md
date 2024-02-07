# RestAPI for a Parts Warehouse
Simple REST API for Parts Warehouse built with FastAPI and MongoDB.

## Endpoints
| Method | Endpoint | Input | Action | Output |
| :-: | - | - | :-: | :-: |
| POST | /part | {<br>"serial_number": [str],<br>"name": [str],<br>"description": [str],<br>"category": [str],<br>"quantity": [int],<br>"price": [float],<br>"location": {<br>&nbsp;&nbsp;&nbsp;"room": [str],<br>&nbsp;&nbsp;&nbsp;"bookcase": [str],<br>&nbsp;&nbsp;&nbsp;"shelf": [int],<br>&nbsp;&nbsp;&nbsp;"cuvette": [int],<br>&nbsp;&nbsp;&nbsp;"column": [int],<br>&nbsp;&nbsp;&nbsp;"row": [int]<br>&nbsp;&nbsp;&nbsp;}<br>} | Add new part | Part |
| GET | /part/<part_id>/ |  | Get part by its ID | Part |
| PUT | /part/<part_id>/ | Selected fields from Add part endpoint.<br>Updating the 'location' field requires providing all subfields. | Update part details | Part |
| DELETE | /part/<part_id>/ |  | Delete part | - |
| GET | /part/search | Query params:<br>-serial_number [str]<br>-name [str]<br>-description [str]<br>-category [str]<br>-min_quantity [int]<br>-max_quantity [int]<br>-min_price [float]<br>-max_price [float]<br>-room [str]<br>-bookcase [str]<br>-shelf [int]<br>-cuvette [int]<br>-column [int]<br>-row [int] | Search parts by params | List of parts that meet all provided criteria |
| GET | /category |  | Get all categories | List of categories |
| POST | /category | {<br>"name": [str],<br>"parent_name": [str]<br>} | Add new category | Category |
| GET | /category/<category_id>/ |  | Get category by its ID | Category |
| PUT | /category/<category_id>/ | Selected fields from Add category endpoint. | Update category details | Category |
| DELETE | /category/<category_id>/ |  | Delete category | - |

## Installation

**1. Clone the repository.**
```
git clone https://github.com/bartekbednarz013/warehouse-API.git
```
**2. Navigate to the 'warehouse-API' directory.**
```
cd warehouse-API
```
**3. Build the container.**
```
docker compose build
```
**4. Run the container.**
```
docker compose up
```
**5. Go to** ```http://127.0.0.1:8000/docs``` **to conveniently browse the API.**