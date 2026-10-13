# ������Լ v1

���� JSON �ļ� UTF-8��ID ��СдӢ�ġ����ֺ����ַ����ļ���������� ID�������� `YYYY-MM-DD`��ʱ���ô�ʱ���� ISO 8601��δ֪����ʱ��Ϊ `null`��������������������ȡʱ�䡣

## Theory (`data/theories/{id}.json`)

`id, name, aliases[], status, summary, source_ids[], claims[], open_questions[], updated_at`��

״̬��`tracked`���������٣���`candidate`����������������`archived`��ֹͣ���٣�������ʷ����
�۵㣺`text, source_ids[], attribution`��attribution Ϊ `author_statement`���˶���ԭ���߱����`secondary_summary`���������ϸ�������`editorial_analysis`�����߷�������ժҪ���ܱ�������֧�ֵķ�Χ����

## Source (`data/sources/{id}.json`)

`id, url, title, author, kind, published_at, discovered_at, checked_at, verification, summary, limitation, supersedes`��

kind��`primary`��`secondary`��`transcript`��verification��`read`���ɺ˶����ģ���`metadata_only`����Ԫ���ݣ���`unavailable`������ʧ�ܣ���
ֻ�� `read` ����֧��ʵ�ʹ۵㣬`primary + read` ����֧�� author_statement��ת�����ָ��Ϊ transcript��������������ԭ��Ƶ���汾�仯������¼��supersedes ����ָ��ͬ URL �ľɼ�¼��

## Event (`data/events/{id}.json`)

`id, date, type, theory_ids[], source_ids[], summary, run_id`��
type��`seed`��`source_added`��`claim_updated`��`theory_added`��`candidate_found`��`correction`�������¼�����������ۡ���Դ��һ�����С�

## Run (`data/runs/{id}.json`)

`id, date, started_at, completed_at, status, coverage_from, coverage_to, checks[], failures[], event_ids[]`��
status��`seed`��`complete`��`partial`��`failed`��
check��`query, outcome, note`��outcome Ϊ `ok`��`failed`��ÿ����������һ�� check��complete Ҫ��ȫ����ѯ�ɹ���failures Ϊ�ա�seed ������Ϊ��������ˮλ��û�з������� event_ids Ϊ�գ���Ҫ˵���������Run �� Event ˫�����á�

## ȥ��

URL ȥ�����ٲ�����������ê�㣬������ʵ���ݱ�ʶ����ͬ��Դ ID ���ظ����ӣ�ͬ URL ͬժҪͬ״̬�ܾ��ظ���ʵ�����ݱ��ʹ���� Source ID��supersedes �� correction/claim_updated �¼������� checked_at �ı�������°汾��
