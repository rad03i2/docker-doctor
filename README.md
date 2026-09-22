# Docker Doctor

A small, deterministic static diagnostic tool for Docker projects. Docker Doctor reviews common `Dockerfile` and Docker Compose configuration risks without invoking Docker, executing project code, or contacting a registry.

> English documentation first. التوثيق العربي الكامل موجود أدناه.

## Why it exists
Docker configuration mistakes are often visible before an image is built: unpinned images, privileged containers, Docker socket mounts, likely inline credentials, or a final image that runs as root. Docker Doctor makes these issues visible in local development and CI with actionable findings and predictable exit codes.

## Key features
- Scans `Dockerfile` / `dockerfile` and common Compose filenames in a project root.
- Detects missing `FROM`, unpinned base/service images, privileged mode, host networking, Docker socket mounts, likely secret-bearing declarations, remote `ADD`, package upgrades, root final images, and selected image-hygiene issues.
- Severity levels: `error`, `warning`, and `info` with stable rule IDs.
- Human-readable output and structured JSON.
- Configurable CI failure threshold with `--fail-on`.
- Reusable Python API.
- Read-only and offline: no Docker daemon, registry, telemetry, or code execution.
- No runtime dependencies; Python standard library only.

## Preview
```text
$ docker-doctor .
Docker Doctor — /workspace/app
Scanned: Dockerfile, compose.yml
[ERROR  ] C001 compose.yml:4 — Service enables privileged mode.
[WARNING] D002 Dockerfile:1 — Base image is not pinned to an explicit tag: ubuntu:latest
Summary: 1 error(s), 1 warning(s), 2 info
```
The exact findings depend on your files. A screenshot is optional because the primary interface is terminal/JSON output.

## Requirements
- Python 3.10 or newer.
- No Docker installation is required for analysis.

## Installation
From a clone:
```bash
git clone https://github.com/rad03i2/docker-doctor.git
cd docker-doctor
python -m pip install -e .
```
For development/testing:
```bash
python -m pip install -e . pytest
```

## Usage
Scan the current project:
```bash
docker-doctor .
```
Machine-readable output:
```bash
docker-doctor . --json
```
Fail CI on warnings or errors:
```bash
docker-doctor . --fail-on warning
```
Report everything without a non-zero finding exit:
```bash
docker-doctor . --fail-on never
```
Exit codes are `0` for a successful scan below the selected threshold, `1` when the threshold is met, and `2` for invalid input/read errors.

## Python API
```python
from docker_doctor import scan_project

report = scan_project(".")
print(report.counts)
for finding in report.findings:
    print(finding.code, finding.severity, finding.message)
```

## Configuration
Docker Doctor intentionally has no hidden config file in v1.0. The scan target and CI threshold are explicit CLI arguments, keeping behavior easy to reproduce. Supported root filenames are `Dockerfile`, `dockerfile`, `compose.yml`, `compose.yaml`, `docker-compose.yml`, and `docker-compose.yaml`.

## Project structure
```text
src/docker_doctor/
  __init__.py       Package API and metadata
  cli.py            Command-line interface
  scanner.py        Dockerfile/Compose diagnostics
tests/
  test_scanner.py   Functional and CLI tests
.github/workflows/
  ci.yml            Cross-platform test matrix
```

## Testing and validation
```bash
python -m compileall -q src tests
pytest -q
docker-doctor --version
```
CI runs these checks on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13. A committed workflow does not by itself prove a particular run passed; check the repository Actions page for live status.

## Security and privacy
Analysis is local and read-only. Docker Doctor does not build images, start containers, invoke the Docker daemon, access registries, or upload configuration. Secret-related rules report the location/type of a suspicious declaration and do not intentionally print extracted credential values. See [SECURITY.md](SECURITY.md).

## Limitations
Docker Doctor is a focused static heuristic checker, not a Dockerfile parser, vulnerability/CVE scanner, malware detector, secret scanner, SBOM generator, policy engine, or runtime security product. Compose analysis is line-oriented rather than a full YAML semantic parse, so anchors, unusual multiline forms, generated configuration, and complex interpolation may evade rules or produce false positives. A warning is not proof of a vulnerability, and some flagged settings are legitimate in constrained environments.

## Optional roadmap
Future work may include opt-in recursive Dockerfile discovery, additional rules with fixtures, SARIF output, and a semantic Compose parser if those additions can preserve deterministic offline behavior.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Please accompany new rules with focused positive and negative tests and actionable remediation text.

## License
MIT — see [LICENSE](LICENSE).

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية

## نظرة عامة
**Docker Doctor** أداة محلية خفيفة لفحص ملفات مشاريع Docker فحصًا ثابتًا وآمنًا. تراجع `Dockerfile` وملفات Docker Compose الشائعة وتعرض مشكلات قابلة للتنفيذ من دون تشغيل Docker أو تنفيذ كود المشروع أو الاتصال بسجل صور خارجي.

## لماذا يوجد المشروع؟
يمكن اكتشاف عدد من أخطاء إعداد Docker قبل البناء، مثل الصور غير المثبتة على إصدار واضح، وتشغيل الحاوية بصلاحيات واسعة، وربط Docker socket، ووجود قيم اعتماد محتملة داخل الإعدادات، أو تشغيل الصورة النهائية كمستخدم root. الهدف هو جعل هذه الحالات واضحة للمطور محليًا وداخل CI مع رموز خروج متوقعة.

## الميزات الرئيسية
- فحص `Dockerfile` و`dockerfile` وأسماء Compose الشائعة في جذر المشروع.
- كشف غياب `FROM`، والصور غير المثبتة، و`privileged`، وشبكة host، وربط Docker socket، وبعض أنماط الأسرار المحتملة، و`ADD` البعيد، وترقية الحزم أثناء البناء، وعدم تحديد مستخدم غير root، وبعض ملاحظات نظافة الصورة.
- مستويات `error` و`warning` و`info` مع معرف ثابت لكل قاعدة.
- إخراج مقروء للبشر أو JSON للأتمتة.
- `--fail-on` لتحديد المستوى الذي يجعل CI يفشل.
- Python API قابلة لإعادة الاستخدام.
- تعمل دون اتصال ولا تحتاج Docker كاعتماد وقت التشغيل، ولا توجد telemetry.

## المتطلبات والتثبيت
تحتاج Python 3.10 أو أحدث فقط. لا تحتاج إلى Docker لإجراء التحليل.
```bash
git clone https://github.com/rad03i2/docker-doctor.git
cd docker-doctor
python -m pip install -e .
```
وللتطوير:
```bash
python -m pip install -e . pytest
```

## الاستخدام
```bash
docker-doctor .
docker-doctor . --json
docker-doctor . --fail-on warning
docker-doctor . --fail-on never
```
رمز الخروج `0` يعني أن الفحص لم يصل إلى عتبة الفشل المختارة، و`1` يعني وجود نتيجة عند العتبة أو أعلى، و`2` يعني خطأ في الإدخال أو القراءة.

## Python API
```python
from docker_doctor import scan_project
report = scan_project(".")
print(report.counts)
```

## الإعداد
لا يوجد ملف إعداد مخفي في الإصدار 1.0. مسار المشروع وعتبة CI صريحان في سطر الأوامر لضمان سلوك سهل التكرار. الأسماء المدعومة في الجذر موثقة في القسم الإنجليزي أعلاه.

## بنية المشروع
المحرك والواجهة موجودان داخل `src/docker_doctor/`، والاختبارات في `tests/`، وCI داخل `.github/workflows/ci.yml`.

## الاختبارات
```bash
python -m compileall -q src tests
pytest -q
docker-doctor --version
```
تم إعداد CI لاختبار Python 3.10 و3.12 و3.13 على Ubuntu وWindows وmacOS. وجود ملف CI لا يعني وحده أن تشغيلًا بعينه نجح؛ راجع صفحة Actions للحالة الفعلية.

## الأمان والخصوصية
الفحص محلي وللقراءة فقط. لا تبني الأداة الصور، ولا تشغل الحاويات، ولا تستدعي Docker daemon، ولا تتصل بالسجلات، ولا ترفع الملفات. قواعد الأسرار تشير إلى موضع ونوع النمط المشبوه ولا تهدف إلى طباعة قيمة سرية مستخرجة. راجع [SECURITY.md](SECURITY.md).

## القيود
هذه الأداة مدقق heuristics ثابت ومحدود، وليست ماسح CVE أو برمجيات خبيثة أو أسرار متكاملًا، وليست مولد SBOM أو محرك سياسات أو أداة حماية وقت التشغيل. تحليل Compose سطري وليس محلل YAML دلاليًا كاملًا، لذلك قد تفوت بعض التركيبات المعقدة أو تظهر نتائج إيجابية كاذبة. التحذير لا يثبت وجود ثغرة، وبعض الإعدادات التي يتم تنبيهك إليها قد تكون مقصودة.

## تطوير اختياري مستقبلًا
يمكن إضافة اكتشاف اختياري لملفات Docker المتداخلة، وقواعد إضافية مع fixtures، وإخراج SARIF، أو تحليل Compose دلالي إذا أمكن الحفاظ على التشغيل المحلي الحتمي.

## المساهمة
راجع [CONTRIBUTING.md](CONTRIBUTING.md). يجب أن ترافق القواعد الجديدة اختبارات واضحة ونصائح معالجة عملية.

## الترخيص
MIT — راجع [LICENSE](LICENSE).

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
