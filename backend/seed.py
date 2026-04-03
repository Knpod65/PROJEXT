"""
Seed data — ข้อมูลจริงจาก Personnel_120226.xlsx
"""
from sqlalchemy.orm import Session
import models
from auth_utils import hash_password


def seed_data(db: Session):
    if db.query(models.User).count() > 0:
        return

    # ── Admin ─────────────────────────────────────────────────
    for uname, email, fname, title_th, ext, mobile, emp_id in [
        ("mathawee.m", "mathawee.m@cmu.ac.th", "มาธวี เมืองศรี",   "นางสาว", "053-941858", "084-9899147", 33),
        ("atikant.s",  "atikant.s@cmu.ac.th",  "อติกานต์ แสงวิลัย","นาย",    "053-941863", "082-8864005", 36),
    ]:
        db.add(models.User(
            username=uname, email=email,
            password_hash=hash_password("admin123"),
            role=models.UserRole.admin,
            full_name=fname, title=title_th,
            division="Education_Student_Quality", unit="Education_Services",
            ext=ext, mobile=mobile, employee_id=emp_id,
        ))

    # ── ESQ Head ──────────────────────────────────────────────
    db.add(models.User(
        username="napaporn.ph", email="napaporn.ph@cmu.ac.th",
        password_hash=hash_password("esq123"),
        role=models.UserRole.esq_head,
        full_name="นภาภรณ์ ปัญญาราษฎร์", title="นางสาว",
        division="Education_Student_Quality", unit="Education_Services",
        ext="053-942981", mobile="081-1112396", employee_id=27,
    ))

    # ── Dept Supervisors ──────────────────────────────────────
    for uname, email, fname, title_th, dept, ext, mobile, emp_id in [
        ("phusanisa.sai",       "phusanisa.sai@cmu.ac.th",       "ภูษณิศา สายคํา",           "นางสาว", "GOV", "053-942984", "065-9469095", 28),
        ("pornchanok.s",        "pornchanok.s@cmu.ac.th",        "พรชนก เสนะสุทธิพันธุ์",    "นางสาว", "IR",  "053-942987", "063-6642923", 29),
        ("rungtiwa.p",          "rungtiwa.p@cmu.ac.th",          "รุ่งทิวา ปาลี",             "นางสาว", "PA",  "053-941851", "084-9503390", 30),
        ("chanikan.phanthuree", "chanikan.phanthuree@cmu.ac.th", "ชนิกานต์ พันธุรี",         "นางสาว", "STB", "053-941854", "063-2073887", 35),
    ]:
        db.add(models.User(
            username=uname, email=email,
            password_hash=hash_password("staff123"),
            role=models.UserRole.dept_supervisor,
            full_name=fname, title=title_th,
            division="Education_Student_Quality", unit="Education_Services",
            dept_code=dept, ext=ext, mobile=mobile, employee_id=emp_id,
        ))

    # ── Staff ─────────────────────────────────────────────────
    staff_rows = [

        ("ketsinee.s",      "ketsinee.s@cmu.ac.th",      "สิรินภัทร สมพงษ์",          "นาง",    "General_Administration",       "Human_Resources",           "053-942960","084-0467759", 2),
        ("napaksurang.t",   "napaksurang.t@cmu.ac.th",   "ณภัคสุรางค์ ธนาณิศสุรางค์","นางสาว", "General_Administration",       "Human_Resources",           "053-942951","085-6158388", 3),
        ("waricha.s",       "waricha.s@cmu.ac.th",       "วริชา สร้อยสวิง",           "นางสาว", "General_Administration",       "Human_Resources",           "053-942996","095-4166239", 4),
        ("ratchaneewan.p",  "ratchaneewan.p@cmu.ac.th",  "รัชนีวรรณ ปัญญาเทพ",       "นางสาว", "General_Administration",       "General_Administration",    "053-942963","086-1792263", 5),
        ("kanokwan.pribwai","kanokwan.pribwai@cmu.ac.th", "กนกวรรณ อุ่นนันกาศ",       "นางสาว", "General_Administration",       "Finance_Supplies",          "053-942956","095-9989595", 6),
        ("nattaya.siri",    "nattaya.siri@cmu.ac.th",    "ณัฐธยาน์ ศิริปัญญา",       "นางสาว", "General_Administration",       "Finance_Supplies",          "053-941865","087-3551853", 7),
        ("wipawee.s",       "wipawee.s@cmu.ac.th",       "ณัฏฐพัชร ศรีรินทร์",       "นางสาว", "General_Administration",       "Finance_Supplies",          "053-941856","093-1594496", 8),
        ("laddaporn.y",     "laddaporn.y@cmu.ac.th",     "ลัดดาภรณ์ ยาบุญนะ",        "นางสาว", "General_Administration",       "Finance_Supplies",          "053-942961","084-0439086", 9),
        ("thitaree.b",      "thitaree.b@cmu.ac.th",      "ฐิตารีย์ บูรณะธนะสิทธิ์", "นางสาว", "General_Administration",       "Finance_Supplies",          "053-942962","094-1200435",10),
        ("chaitri.s",       "chaitri.s@cmu.ac.th",       "ชัยตรี ศรีใจ",              "นาย",    "General_Administration",       "Audio_Visual_Environment",  "053-942998","089-8508260",11),
        ("thanapat.p",      "thanapat.p@cmu.ac.th",      "ธนภัทร ปัญญาวุฒิ",         "นาย",    "General_Administration",       "Audio_Visual_Environment",  "053-942997","081-1658940",12),
        ("chanachon.th",    "chanachon.th@cmu.ac.th",    "ชนะชล ทรฤทธิ์",            "นาย",    "General_Administration",       "Audio_Visual_Environment",  "053-942965","098-7757795",13),
        ("thiraphan.y",     "thiraphan.y@cmu.ac.th",     "ธีราภัณฑ์ ยะโสภา",         "นาง",    "General_Administration",       "Audio_Visual_Environment",  "053-942965","083-2033180",14),
        ("kraipol.p",       "kraipol.p@cmu.ac.th",       "ไกรพล ปัญญาสุ",            "นาย",    "Strategic_Planning",           "Strategy_Quality_Assurance","053-942957","080-0322003",15),
        ("veeraphat.han",   "veeraphat.han@cmu.ac.th",   "วีรภัทร์ หาญสุข",           "นาย",    "Strategic_Planning",           "Strategy_Quality_Assurance","053-941857","094-6423995",16),
        ("isaree.ph",       "isaree.ph@cmu.ac.th",       "อิสรีย์ พงศ์ทิวาพรรณ",     "นางสาว", "Strategic_Planning",           "Strategy_Quality_Assurance","053-941862","083-5827277",17),
        ("sarat.khattiya",  "sarat.khattiya@cmu.ac.th",  "สารัตถ์ ขัตติยะ",           "นาย",    "Strategic_Planning",           "IT_Communication",          "053-942959","085-7149493",18),
        ("wachiravut.ya",   "Wachiravut.ya@cmu.ac.th",   "วชิราวุธ ยาเก๋",            "นาย",    "Strategic_Planning",           "IT_Communication",          "053-941860","098-7509182",19),
        ("pitcharee.l",     "pitcharee.l@cmu.ac.th",     "พิชชารีย์ ลิ่วเกียรติ",    "นางสาว", "Political_Innovation_Center",  "",                          "053-941877","090-6746110",20),
        ("sakawkawin.kan",  "sakawkawin.kan@cmu.ac.th",  "สกาวกวิน กาญจนเสมา",       "นางสาว", "Political_Innovation_Center",  "",                          "053-941877","096-2352658",21),
        ("sosittha.s",      "sosittha.s@cmu.ac.th",      "โศศิษฐา ศรีสุข",            "นางสาว", "Political_Innovation_Center",  "",                          "053-941855","065-6966535",22),
        ("rapattra.h",      "rapattra.h@cmu.ac.th",      "รภัทรา หิรัญรังสิต",        "นางสาว", "Research_Academic_Services",   "Research_HEAD",                  "053-942985","089-7574772",23),
        ("sirima.ch",       "sirima.ch@cmu.ac.th",       "สิริมา ชินสมุทร",           "นางสาว", "Research_Academic_Services",   "Research",                  "053-942995","091-8592917",24),
        ("kotchakarn.th",   "kotchakarn.th@cmu.ac.th",   "กชกานต์ ทองรัตน์",         "นางสาว", "Research_Academic_Services",   "Academic_Services",         "053-941861","089-1586930",25),
        ("supheerutai.b",   "supheerutai.b@cmu.ac.th",   "สุภีฤทัย บัวแก้ว",          "นางสาว", "Research_Academic_Services",   "International_Relations",   "053-942958","083-5676591",26),
        ("araya.fa",        "araya.fa@cmu.ac.th",        "อารยา ฟ้ารุ่งสาง",          "นางสาว", "Education_Student_Quality",    "Education_Services",        "053-942983","087-7868456",31),
        ("sapanyu.wong",    "sapanyu.wong@cmu.ac.th",    "สัพพัญญู วงศ์ชัย",          "นาย",    "Education_Student_Quality",    "Education_Services",        "053-941853","085-5322834",32),
        ("warinthorn.s",    "warinthorn.s@cmu.ac.th",    "วรินทร สมฟอง",              "นางสาว", "Education_Student_Quality",    "Education_Services",        "053-941852","094-3435011",34),
        ("ketdao.l",        "ketdao.l@cmu.ac.th",        "เกตุดาว หลงลืม",            "นางสาว", "Education_Student_Quality",    "Student_Development",       "053-942964","095-6877152",37),
    ]
    staff_objs = {}
    for (uname, email, fname, title_th, division, unit, ext, mobile, emp_id) in staff_rows:
        u = models.User(
            username=uname, email=email,
            password_hash=hash_password("staff123"),
            role=models.UserRole.staff,
            full_name=fname, title=title_th,
            division=division, unit=unit,
            ext=ext, mobile=mobile, employee_id=emp_id,
        )
        db.add(u)
        staff_objs[uname] = u
    db.flush()

    # ── Teachers ──────────────────────────────────────────────
    teacher_rows = [
        # GOV
        ("pailin.phu",         "pailin.phu@cmu.ac.th",         "ไพลิน ภู่จีนาพันธุ์",       "รศ.ดร.", "GOV", "42950",     "083-6119933",  1),
        ("chanintorn.p",       "chanintorn.p@cmu.ac.th",       "ชนินทร เพ็ญสูตร",           "รศ.ดร.", "GOV", "42954",     "098-6565342",  2),
        ("nattapon.t",         "nattapon.t@cmu.ac.th",         "ณัฐพล ตันตระกูลทรัพย์",    "ผศ.ดร.", "GOV", "42989#128", "085-0422404",  3),
        ("malinee.k",          "malinee.k@cmu.ac.th",          "มาลินี คุ้มสภา",             "ผศ.ดร.", "GOV", "42990",     "081-4407042",  4),
        ("supitcha.pu",        "supitcha.pu@cmu.ac.th",        "สุพิชฌาย์ ปัญญา",           "ผศ.ดร.", "GOV", "42989#129", "094-6356219",  5),
        ("wanpat.young",       "wanpat.young@cmu.ac.th",       "วันพัฒน์ ยังมีวิทยา",       "ผศ.ดร.", "GOV", "42989#133", "084-3267449",  6),
        ("ram.joti",           "ram.joti@cmu.ac.th",           "ราม โชติคุต",                "ผศ.",    "GOV", "42999#117", "093-7282227",  7),
        ("panuwat.p",          "panuwat.p@cmu.ac.th",          "ภาณุวัฒน์ พันธุ์ประเสริฐ",  "ผศ.ดร.", "GOV", "42999#122", "094-6987185",  8),
        ("nuttakorn.vit",      "nuttakorn.vit@cmu.ac.th",      "ณัฐกร วิทิตานนท์",          "ผศ.ดร.", "GOV", "42989#147", "089-4296999",  9),
        ("chatthip.ch",        "chatthip.ch@cmu.ac.th",        "ฉัตรทิพย์ ชัยฉกรรจ์",      "ผศ.ดร.", "GOV", "42999#115", "088-8709550", 10),
        ("thannapat.j",        "thannapat.j@cmu.ac.th",        "ธัญณ์ณภัทร์ เจริญพานิช",   "ผศ.ดร.", "GOV", "42989#147", "094-6349751", 11),
        ("pinsuda.w",          "pinsuda.w@cmu.ac.th",          "พินสุดา วงศ์อนันต์",         "อ.",     "GOV", "42999#105", "095-6751413", 12),
        ("pornchanok.rueng",   "pornchanok.rueng@cmu.ac.th",   "พรชนก เรืองวีรยุทธ",        "อ.ดร.", "GOV", "42989#127", "062-5399355", 13),
        ("nisanee.c",          "nisanee.c@cmu.ac.th",          "ณิศนีญ์ ชัยประกอบวิริยะ",  "อ.",     "GOV", "42989#147", "091-8838643", 14),
        ("manita.n",           "manita.n@cmu.ac.th",           "มานิตา หนูสวัสดิ์",          "อ.ดร.", "GOV", "42999#113", "089-4433856", 15),
        # PA
        ("thanyawat.r",        "thanyawat.r@cmu.ac.th",        "ธันยวัฒน์ รัตนสัค",         "รศ.ดร.", "PA", "42999#110", "091-0677532", 16),
        ("panom.gunawong",     "panom.gunawong@cmu.ac.th",     "พนม กุณาวงค์",               "รศ.ดร.", "PA", "42999#121", "081-3075502", 17),
        ("thitiwut.boonya",    "thitiwut.boonya@cmu.ac.th",    "ฐิติวุฒิ บุญยวงศ์วิวัชร",   "รศ.ดร.", "PA", "42999#124", "097-9325445", 18),
        ("siripong.lad",       "siripong.lad@cmu.ac.th",       "ศิริพงษ์ ลดาวัลย์ ณ อยุธยา","รศ.",    "PA", "42999#104", "084-6875175", 19),
        ("udomchoke.a",        "udomchoke.a@cmu.ac.th",        "อุดมโชค อาษาวิมลกิจ",       "ผศ.ดร.", "PA", "42989#141", "062-2945252", 20),
        ("pojjana.p",          "pojjana.p@cmu.ac.th",          "พจนา พิชิตปัจจา",            "ผศ.ดร.", "PA", "42989#134", "081-7835828", 21),
        ("patamawadee.j",      "patamawadee.j@cmu.ac.th",      "ปฐมาวดี จงรักษ์",           "รศ.ดร.", "PA", "42999#103", "064-9469547", 22),
        ("raweewan.patsamarn", "raweewan.patsamarn@cmu.ac.th", "รวีวรรณ แพทย์สมาน",         "ผศ.ดร.", "PA", "42989#135", "089-6357226", 23),
        ("kraiwuth.j",         "kraiwuth.j@cmu.ac.th",         "ไกรวุฒิ ใจคําปัน",           "ผศ.ดร.", "PA", "42989#137", "095-6759775", 24),
        ("alongkorn.k",        "alongkorn.k@cmu.ac.th",        "อลงกรณ์ คูตระกูล",           "ผศ.ดร.", "PA", "42953",     "091-7919455", 25),
        ("worrapong.t",        "worrapong.t@cmu.ac.th",        "วรพงศ์ ตระการศิรินนท์",     "ผศ.ดร.", "PA", "42999#108", "081-3508095", 26),
        ("pikul.i",            "pikul.i@cmu.ac.th",            "พิกุล อิทธิหิรัญวงศ์",       "อ.",     "PA", "42989#132", "061-6283491", 27),
        ("sasipatch.c",        "sasipatch.c@cmu.ac.th",        "ศศิพัชร์ ชัยสิริบดินทร์",   "อ.ดร.", "PA", "42999#102", "096-2939553", 28),
        ("orachorn.s",         "orachorn.s@cmu.ac.th",         "อรชร แซ่จาง",                "อ.ดร.", "PA", "42989#139", "094-3925472", 29),
        ("natthapong.pak",     "natthapong.pak@cmu.ac.th",     "นัทธพงศ์ ปกีรณัม",          "อ.ดร.", "PA", "42989#126", "096-8909361", 30),
        # IR
        ("paruedee.ngui",      "paruedee.ngui@cmu.ac.th",      "พฤดี หงุ่ยตระกูล",          "รศ.ดร.", "IR", "42989#131", "092-0926186", 31),
        ("wannapa.l",          "wannapa.l@cmu.ac.th",           "วรรณภา ลีระศิริ",            "ผศ.ดร.", "IR", "42989#140", "099-4584448", 32),
        ("kiancheng.lee",      "kiancheng.lee@cmu.ac.th",      "LEE KIAN CHENG",             "ผศ.ดร.", "IR", "42999#114", "086-1965400", 33),
        ("achara.b",           "achara.b@cmu.ac.th",           "อัจฉรา บรรจงประเสริฐ",      "ผศ.ดร.", "IR", "42999#107", "084-6479750", 34),
        ("kanyanattha.i",      "kanyanattha.i@cmu.ac.th",      "กัญญณัฏฐา อิทธินิติวุฒิ",  "ผศ.ดร.", "IR", "42999#109", "092-2353599", 35),
        ("narut.c",            "narut.c@cmu.ac.th",            "นรุตม์ เจริญศรี",             "ผศ.ดร.", "IR", "42999#123", "081-3462927", 36),
        ("benjamas.n",         "benjamas.n@cmu.ac.th",         "เบญจมาศ นิลสุวรรณ์",        "ผศ.ดร.", "IR", "42999#119", "082-8917585", 37),
        ("pichaarpa.p",        "pichaarpa.p@cmu.ac.th",        "พิชญ์อาภา พิศุทธ์เศรณี",   "ผศ.ดร.", "IR", "42999#116", "081-9603522", 38),
        ("matthew.r",          "matthew.r@cmu.ac.th",          "Matthew Robson",             "อ.ดร.", "IR", "42989#125", "085-5658255", 39),
        ("kamonphorn.k",       "kamonphorn.k@cmu.ac.th",       "กมลพร กัญชนะ",               "อ.ดร.", "IR", "42999#112", "089-2658686", 40),
        ("atchareeya.s",       "atchareeya.s@cmu.ac.th",       "อัจฉรียา สายศิลป์",          "อ.ดร.", "IR", "42989#130", "081-7168779", 41),
        ("sirada.khe",         "sirada.khe@cmu.ac.th",         "ศิรดา เขมานิฏฐาไท",         "อ.ดร.", "IR", "42999#106", "089-6966286", 42),
        ("pran.jin",           "pran.jin@cmu.ac.th",           "ปราน จินตะเวช",              "อ.ดร.", "IR", "42989#138", "096-9182268", 43),
        # STB
        ("witchuda.s",         "witchuda.s@cmu.ac.th",         "วิชชุดา สร้างเอี่ยม",        "อ.ดร.", "STB","42999#120", "086-4541426", 44),
    ]
    teacher_objs = {}
    for (uname, email, fname, title_th, dept_code, ext, mobile, t_id) in teacher_rows:
        t = models.User(
            username=uname, email=email,
            password_hash=hash_password("teacher123"),
            role=models.UserRole.teacher,
            full_name=fname, title=title_th,
            dept_code=dept_code, department=dept_code,
            ext=ext, mobile=mobile, employee_id=t_id,
        )
        db.add(t)
        teacher_objs[uname] = t
    db.flush()

    # ── Rooms ─────────────────────────────────────────────────
    rooms_data = [
        ("PSB 1101",        "PSB",        60,  "PSB1101"),
        ("PSB 1204",        "PSB",        40,  "PSB1204"),
        ("PSB 1307",        "PSB",        40,  "PSB1307"),
        ("Auditorium 50ปี", "อาคาร 50ปี", 200, "AUD50"),
    ]
    room_objs = {}
    for rname, building, cap, ecode in rooms_data:
        r = models.Room(room_name=rname, building=building, capacity=cap, e_room_code=ecode)
        db.add(r)
        room_objs[rname] = r
    db.flush()

    # ── Courses ───────────────────────────────────────────────
    courses_data = [
        ("126101", "การเมืองการปกครองไทย",        "Thai Politics and Government",          3),
        ("126102", "การเมืองการปกครองเปรียบเทียบ", "Comparative Politics",                  3),
        ("126211", "ทฤษฎีการเมือง",               "Political Theory",                      3),
        ("126217", "การเมืองระหว่างประเทศ",        "International Politics",                3),
        ("126324", "กฎหมายรัฐธรรมนูญ",            "Constitutional Law",                    3),
        ("127100", "รัฐประศาสนศาสตร์เบื้องต้น",    "Introduction to Public Administration", 3),
        ("127202", "การบริหารรัฐกิจ",              "Public Administration",                 3),
        ("128305", "นโยบายสาธารณะ",               "Public Policy",                         3),
        ("131103", "ความสัมพันธ์ระหว่างประเทศ",    "International Relations",               3),
    ]
    course_objs = {}
    for cid, th, en, cred in courses_data:
        c = models.Course(course_id=cid, course_name_th=th, course_name_en=en,
                          credits=cred, department="คณะรัฐศาสตร์ฯ")
        db.add(c)
        course_objs[cid] = c
    db.flush()

    # ── Sections + Schedules ──────────────────────────────────
    sections_data = [
        ("126101","1",  "sirada.khe",   83, "2569-03-23","12.00-15.00","PSB 1101",        "sirada.khe",   "isaree.ph",     "ชนิกานต์ พันธุรี",  15),
        ("126101","2",  "benjamas.n",   67, "2569-03-23","12.00-15.00","Auditorium 50ปี", "benjamas.n",   "waricha.s",     "ชนิกานต์ พันธุรี",  15),
        ("126101","5",  "achara.b",     66, "2569-03-23","12.00-15.00","PSB 1101",        "achara.b",     "rungtiwa.p",    "ชนิกานต์ พันธุรี",  15),
        ("126102","1",  "paruedee.ngui",103,"2569-03-28","12.00-15.00","Auditorium 50ปี", "paruedee.ngui","wipawee.s",     "วชิราวุธ ยาเก๋",     3),
        ("126211","1",  "narut.c",      105,"2569-03-26","15.30-18.30","Auditorium 50ปี", "narut.c",      "thanapat.p",    "อติกานต์ แสงวิลัย", 10),
        ("126217","1",  "kiancheng.lee", 73,"2569-03-24","08.00-11.00","PSB 1101",        "kiancheng.lee","isaree.ph",     "วรินทร สมฟอง",      19),
        ("126324","1",  "kanyanattha.i",102,"2569-03-27","12.00-15.00","Auditorium 50ปี", "kanyanattha.i","pitcharee.l",   "วชิราวุธ ยาเก๋",     3),
        ("127100","1",  "nattapon.t",   71, "2569-03-26","12.00-15.00","PSB 1204",        "nattapon.t",   "napaksurang.t", "วีรภัทร์ หาญสุข",   12),
        ("127100","801","nisanee.c",    148,"2569-03-26","12.00-15.00","Auditorium 50ปี", "nisanee.c",    "witchuda.s",    "วชิราวุธ ยาเก๋",    12),
        ("127202","1",  "wanpat.young", 95, "2569-03-20","15.30-18.30","Auditorium 50ปี", "wanpat.young", "mathawee.m",    "สัพพัญญู วงศ์ชัย",   7),
        ("128305","1",  "udomchoke.a",  30, "2569-03-19","15.30-18.30","PSB 1101",        "udomchoke.a",  "sirima.ch",     "",                   3),
        ("128305","2",  "patamawadee.j",43, "2569-03-19","15.30-18.30","PSB 1101",        "patamawadee.j","araya.fa",      "",                   3),
        ("131103","701","witchuda.s",   37, "2569-03-23","15.30-18.30","PSB 1204",        "witchuda.s",   "mathawee.m",    "",                  11),
    ]

    for (cid, sec_no, t_key, n_stu, ex_date, ex_time, room_name,
         sup1_key, sup2_key, dist, pages) in sections_data:
        course  = course_objs[cid]
        teacher = teacher_objs.get(t_key)
        room    = room_objs.get(room_name)

        section = models.Section(
            course_id=course.id,
            section_no=sec_no,
            teacher_id=teacher.id if teacher else None,
            num_students=n_stu,
            semester="2", academic_year="2568",
        )
        db.add(section)
        db.flush()

        sch = models.ExamSchedule(
            section_id=section.id,
            room_id=room.id if room else None,
            exam_date=ex_date, exam_time=ex_time,
            exam_type=models.ExamType.final,
            status=models.ScheduleStatus.published,
            num_pages=pages, total_sheets=n_stu * pages,
            paper_distributor=dist if dist else None,
        )
        db.add(sch)
        db.flush()

        for slot, skey, comp in [(1, sup1_key, 300.0), (2, sup2_key, 200.0)]:
            u = teacher_objs.get(skey) or staff_objs.get(skey)
            if u:
                db.add(models.Supervision(
                    schedule_id=sch.id, user_id=u.id,
                    slot_order=slot, compensation=comp, confirmed=True
                ))

    db.commit()

    # ── ตั้ง special_role ─────────────────────────────────────
    ROOM_KEEPERS = ["chanachon.th", "thiraphan.y"]   # เปิด/ปิดห้อง
    ESQ_STAFF    = []   # ไม่มี esq_staff พิเศษ — อารยา+สัพพัญญู = staff ปกติ

    for username, srole in (
        [(u, "room_keeper") for u in ROOM_KEEPERS] +
        [(u, "esq_staff")   for u in ESQ_STAFF]
    ):
        u = db.query(models.User).filter(models.User.username == username).first()
        if u:
            u.special_role = srole
    db.commit()
    print(f"  Special roles: {len(ROOM_KEEPERS)} room_keepers (ธีราภัณฑ์+ชนะชล)")
    print("Seed completed: 82 users (2 admin, 1 esq_head, 1 secretary, 4 dept_supervisor, 30 staff, 44 teacher)")
