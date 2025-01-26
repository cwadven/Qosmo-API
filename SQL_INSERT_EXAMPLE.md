## 부탁

너가 계속 이상하게 만들어서 다 지웠어 다시 처음부터 시작하자.

@0_CREATE_RULE_STRUCTURE.md @1_CREATE_RULE_MAP.md @2_CREATE_RULE_NODE.md @3_CREATE_RULE_NODE_COMPLETE_RULE.md @4_CREATE_RULE_QUESTION.md @5_CREATE_RULE_SELF_ARROW.md @6_CREATE_RULE_ARROW.md 

- md 파일에 있는 내용을 제발 참고해줘.
- 만들 때, 내용을 잘 보고 체크리스트에 있는 것들을 참고해서 작성해줘
- md 파일 내부에 있는 체크리스트를 그대로 제대로 완료했는지를 기록하는 파일이랑 sql 각각 만들어줘.
만약 체크리스트를 해결하지못하면 다시 참고해서 수정하면서 작성하고.

"원하는 Map 이름" 100개의 Node 를 가지고 있는 Map 을 만들어줘. 폴더 안에 .sql 파일을 만들어줘

## 기록용

[ 생성 ]

docker cp ./nosql_escape/sql/* checker_postgresql14:/home/

psql  -U postgres -d checker_database -f 00_map.sql
psql  -U postgres -d checker_database -f 01_nodes.sql
psql  -U postgres -d checker_database -f 02_node_complete_rules.sql
psql  -U postgres -d checker_database -f 03_questions.sql
psql  -U postgres -d checker_database -f 04_self_arrows.sql
psql  -U postgres -d checker_database -f 05_arrows.sql

sudo -u postgres psql -d qosmo_database -f 00_map.sql
sudo -u postgres psql -d qosmo_database -f 01_nodes.sql
sudo -u postgres psql -d qosmo_database -f 02_node_complete_rules.sql
sudo -u postgres psql -d qosmo_database -f 03_questions.sql
sudo -u postgres psql -d qosmo_database -f 04_self_arrows.sql
sudo -u postgres psql -d qosmo_database -f 05_arrows.sql


[ 초기화 ]

delete from map_arrow where map_id = 12;
delete from map_nodecompleterule where map_id = 12;
delete from map_node where map_id = 12;
delete from question_question where map_id = 12;
delete from map_mapcategory where map_id = 12;
delete from map_map where id = 12;
