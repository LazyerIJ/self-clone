<div align="center">

[English](README.md) · **한국어**

# self-clone

### 에이전트에게 내 일을 가르치고, 시험까지 통과시킨다.

**레포의 하네스는 코드를 안다. 아무도 *나*를 모른다. self-clone은 안다.**

[![Claude Code skill](https://img.shields.io/badge/Claude_Code-plugin-1b1b19?style=flat-square&logo=claude&logoColor=white)](#설치)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-SKILL.md-1b1b19?style=flat-square)](https://agentskills.io)
[![Python stdlib only](https://img.shields.io/badge/dependencies-0-1b1b19?style=flat-square)](#요구-사항)
[![Read-only](https://img.shields.io/badge/sources-read--only-1b1b19?style=flat-square)](#절대-하지-않는-것)
[![MIT](https://img.shields.io/badge/license-MIT-1b1b19?style=flat-square)](LICENSE)

[빠른 시작](#빠른-시작) · [다 자란 노드](#다-자란-노드) · [시험 루프](#시험-루프) · [동작](#동작) · [FAQ](#faq)

<code>/plugin marketplace add LazyerIJ/self-clone</code>

<br /><br />

<img src="docs/demo.svg" width="860" alt="예시 실행: /loop /grow가 지식 트리를 한 노드씩 키우고, /exam이 트리만 보고 지난 실제 티켓을 풀어 14/25점을 받고, 구멍을 키운 뒤 재시험에서 23/25점을 받는다." />

</div>

---

일하는 레포마다 이미 코드를 아는 Claude 하네스(`CLAUDE.md`·스킬·문서)가 있다. 어느 하네스도 모르는 것은 **키보드 앞의 사람**이다. 일이 어디서 들어오고, 그 일에 어느 레포·스킬을 여는지, 하네스 밖에서 손으로 치는 명령, 누구에게 묻는지, 하네스가 멈춰 나를 기다리는 순간에 무엇을 기준으로 정하는지.

self-clone은 이미 내 컴퓨터에 남은 흔적(Claude 세션·셸 기록·작업 노트·git 로그·티켓·채팅 스레드)에서 그 지식을 **깊고 좁은 트리**로 키운다. 그리고 **트리를 시험한다**. *트리만* 읽을 수 있는 서브에이전트가 지난 실제 티켓을 다시 풀고, 내가 실제로 한 일과 대조해 채점받는다. 빈 곳은 전부 트리에 되꽂혀 다음에 자란다.

루프로 돌리면 끝나지 않는다. 그저 계속 나에게 가까워진다.

## 빠른 시작

```
/plugin marketplace add LazyerIJ/self-clone
/plugin install self-clone@self-clone
/clone-init
```

`/clone-init`은 다섯 가지를 묻고(홈 폴더·이름·레포가 있는 곳·노트 폴더·절대 읽지 않을 폴더) **클론 홈**을 만든다. 원격 없는 로컬 git 폴더다. 그다음:

```
cd ~/self-clone-home && claude
/survey          # 원천 지도: 레포·세션·셸, 그리고 닿는 이슈 트래커·채팅·위키
/loop /grow      # 한 걸음에 노드 하나씩 계속. grow 10번마다 /exam이 알아서 올라온다
```

특정 건을 넣고 싶으면 `/grow ACME-412`나 `/grow <채팅 스레드 링크>`. 그 건을 끝까지 따라가 걸리는 노드마다 꽂는다.

## 다 자란 노드

[`examples/acme`](examples/acme/tree/work/bugs/regression/bisect/local-repro/first-bad-commit/_branch.md)의 settled 끝 노드다. 가상 인물 Alex의 것이다.

```markdown
## Run
- where: `~/code/acme-api`, clean tree (`git stash -u` first if dirty)
- what: `git bisect start main <last-good-tag> && git bisect run make test-fast TEST=<failing test>`
- judge: lands on a dependency bump → stop, go to `culprit-handoff` (Priya owns deps);
         lands on a migration → never re-run it locally, ask the acme-api harness what <sha> changes
- leave: comment on the ticket `first bad: <sha> (<author>), found by bisect`, then `git bisect reset`

## Cases
- ACME-412 (2026-08): CSV export lost the header row → bisect hit a pandas bump → handed to Priya → fixed same day
- ACME-431 (2026-09): `/orders` 30% slower → bisect hit Alex's own N+1 → asked the harness for a fix → merged next morning

## Exam
- Q: Bisect lands on a dependency bump. What now? A: Stop — hand it to Priya with the sha.
```

코드는 한 줄도 옮기지 않는다. 트리에는 **무엇이 어디 있고, 언제 열고, 누구에게 묻고, 어떻게 판단하는지**만 있고, 하네스가 이미 아는 것은 하네스를 가리킨다.

### 팀이 쓰는 도구와도 함께 쓸 수 있다

일이 Slack·Jira·GitLab·Confluence·Sentry를 오간다면, MCP 서버나 CLI로 연결해 두기만 하면 `/survey`가 찾아낸다. 도구마다 이야기의 한 조각(스레드의 요청, 티켓, 머지 리퀘스트, 알림)을 들고 있는데, `/grow`가 한 건을 그 전부에 걸쳐 따라가서 *요청이 첫 메시지부터 마지막 회신까지 어떻게 흘러가는지*를 트리가 배운다. 읽기만 한다. 메시지·코멘트·상태 변경·머지는 하지 않는다.

이렇게 키운 실제 트리 하나는 `/loop /grow` 사흘 만에 노드 약 750개, 실제 사례 약 430개, 시험 문항 약 1,100개가 됐다.

## 시험 루프

"에이전트 메모리"는 대부분 검증되지 않는다. 여기서는 grow 10번마다 frontier가 `@exam`을 올린다.

1. **실제 일 고르기**: 지난 티켓 재연(처음 들어온 요청만 보여 준다), 문제 은행의 시나리오, 또는 트리의 가장 약한 곳을 찌르는 새 질문.
2. **트리만 보고 답하기**: Explore 서브에이전트는 트리가 가리키는 경로만 열 수 있다. 빠진 단계는 `[not in tree]`, 불확실한 건 `[guess]`, 코드 질문은 `[harness: <레포> — <물을 말>]`로 넘긴다.
3. **원천으로 채점**: 정확·실행·판단·사람·완결, 축마다 0~5점. **22/25 이상이고 `[not in tree]`·`[guess]`가 없으면** "대체 가능"이다.
4. **구멍 꽂기**: 빈 곳마다 그것이 살 노드의 `## Unknown`에 꽂고, settled였던 노드는 growing으로 내린다. `/grow`는 `[exam]` 구멍부터 메운다.

[시험 기록 예시](examples/acme/exams/log/2026-10-02-1410-R-checkout-500.md): 14/25 → grow 4번 → 23/25.

## 동작

| 스킬 | 하는 일 |
|---|---|
| `/clone-init` | 클론 홈을 만든다: `tree/`·`tools/`·`sources/`·`exams/`·`RULES.md` |
| `/survey` | 로컬 원천과 닿는 외부 시스템을 지도로 만든다. 자격을 스스로 싣는 도구로만 닿는다 |
| `/grow` | 부를 때마다 **노드 하나**를 키운다: 원천을 끝까지 읽고, 한 층 내려 쪼개거나 바닥 시험을 채운다 |
| `/exam` | 위의 시험 루프 |

**코드는 모양, 내용은 모델.** `tools/tree.py`(파이썬 표준 라이브러리만)는 깊고 좁은 모양을 강제한다(가지당 자식 ≤ 3, 자식 하나짜리 가지 금지, 본문 ≤ 40줄, 층마다 갈래 기준 하나). 다음 걸음도 고른다: 모양 위반 → 시험 구멍 → 꽂힌 사례 → 바닥 미달 → stub → 모름 → 오래된 노드. 무엇을 어디 둘지는 Claude가 정한다.

**바닥 시험.** 끝 노드는 *하나이고*, *그대로 할 수 있고*(정확한 명령·경로·채널·판단 규칙, 또는 "`<레포>` 하네스에 <무엇을> 묻는다"), *틀리지 않고*(적은 사실은 다 열어 확인), 충분히 깊고, `## Run`·포인터 달린 실제 `## Cases` 둘·`## Exam` 문답 셋이 있고 `## Unknown`이 비어야 `settled`다.

```
tree/
├── work/       무엇을 하나       → bugs/regression/bisect/local-repro/first-bad-commit
├── practice/   어떻게 판단하나   → approvals/reviewer-choice/…
├── systems/    무엇을 대상으로   → 지도: 레포·하네스·문서·주인·알림
├── env/        어디서 무엇으로   → devices/laptop/ssh/jump-host
└── org/        누구와            → colleagues/design/<사람>/review-request
```

## 절대 하지 않는 것

- **비밀 읽기**: `.env*`·키·토큰은 읽기가 막혀 있다. 자격이 있다는 사실만 적는다
- **클론 홈 밖에 쓰기**: 원천 레포·외부 시스템은 읽기 전용이다. 커밋·코멘트·메시지·상태 변경 없음
- **고객·개인 데이터 저장**, 채팅·티켓 본문 인용
- **이미 글로 있는 것 복제**: 코드·문서·위키는 포인터만 남긴다
- **내 컴퓨터 밖으로 나가기**: 클론 홈에는 git 원격이 없고, 웹 검색을 막아 사내 이름이 바깥 검색에 들어가지 않는다

## 설치

**Claude Code** (권장)
```
/plugin marketplace add LazyerIJ/self-clone
/plugin install self-clone@self-clone
```

**skills CLI**
```
npx skills add https://github.com/LazyerIJ/self-clone
```

**수동**: `skills/*`를 `~/.claude/skills/`에 복사한다.

스킬은 [Agent Skills](https://agentskills.io) `SKILL.md` 형식을 따른다. Claude Code에서 만들고 시험했다. `/exam`은 Claude Code의 서브에이전트와 `/loop`를 쓰므로, 다른 에이전트에서는 손봐야 할 수 있다.

## 요구 사항

Claude Code · Python 3.9+ (표준 라이브러리만) · git.

## 설정

- `tools/shape.json`: 모든 한도(깊이·가지 수·바닥 시험·재방문 주기·시험 빈도)와 절 제목 자체. `## What`을 `## 무엇`처럼 어떤 언어로든 바꿀 수 있다.
- `clone.json`: 이름, 작업 루트, 하네스 산출물 폴더, 노트 폴더, 읽지 않을 폴더.
- `RULES.md`: 클론이 따르는 헌법. 고쳐 써도 된다.

## FAQ

**그냥 큰 `CLAUDE.md`나 메모리 파일 아닌가?**
아니다. 메모리는 옆으로 쌓이고 검증되지 않는다. 이 트리는 깊게 내려가도록 강제되고(층마다 갈래 기준 하나, "끝"이라 하기 전 바닥 시험), 이미 글로 있는 것은 옮기지 않으며, 시험이 어디가 틀렸는지 계속 증명한다.

**뭔가 업로드되나?**
평소 Claude Code 세션 외에는 없다. 클론 홈은 원격 없는 로컬 git 폴더이고, 생성되는 권한 설정이 웹 검색·`git push`·비밀 읽기를 막는다.

**쓸 만해지기까지 얼마나 걸리나?**
첫 `/survey`와 grow 수십 번이면 쓸 만한 지도가 된다. 기준은 지난 실제 티켓 재연에서 "대체 가능"이 나오는 것이고, 거기까지 얼마나 남았는지는 시험 기록이 정직하게 알려 준다.

**개발 말고 다른 일에도 쓸 수 있나?**
쓸 수 있다. 측면(work·practice·systems·env·org)은 어떤 사무 직무에도 맞는다. `tree/`와 `RULES.md`에서 이름을 바꾸면 된다.

## 라이선스

MIT
