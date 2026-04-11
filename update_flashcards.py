#!/usr/bin/env python3
import json
import re

# Read the HTML file
with open('/Users/tranmanh/Desktop/LEARN/bjt/BJT_Learning_Hub.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Data for updating Văn bản thương mại entries
updates = {
    "注文書": {
        "explain": "注文(đặt hàng) + 書(tài liệu): tài liệu chính thức từ khách hàng yêu cầu mua hàng",
        "example": "注文書を確認してから商品を発送します",
        "exampleReading": "ちゅうもんしょをかくにんしてからしょうひんをはっそうします"
    },
    "発注書": {
        "explain": "発注(phát lệnh đặt hàng) + 書(phiếu): công ty phát hành để yêu cầu cung cấp hàng từ nhà cung cấp",
        "example": "発注書に記載された数量を確認しました",
        "exampleReading": "はっちゅうしょにきさいされたすうりょうをかくにんしました"
    },
    "稟議書": {
        "explain": "稟議(trình cấp trên xin phê duyệt) + 書(tài liệu): công ty gửi cấp trên xin phê duyệt dự án, chi phí",
        "example": "新しいプロジェクトの稟議書を提出しました",
        "exampleReading": "あたらしいぷろじぇくとのりんぎしょをていしゅつしました"
    },
    "始末書": {
        "explain": "始末(chi tiết sự vật từ đầu đến cuối) + 書(tài liệu): tài liệu giải thích chi tiết về sai lầm, sự cố",
        "example": "仕事上のミスについて始末書を作成する",
        "exampleReading": "しごとじょうのみすについてしまつしょをさくせいする"
    },
    "顛末書": {
        "explain": "顛末(sự vật từ đầu đến cuối) + 書(báo cáo): báo cáo toàn bộ quá trình và kết quả của sự việc",
        "example": "トラブルの顛末書を提出する必要があります",
        "exampleReading": "とらぶるのてんまつしょをていしゅつするひつようがあります"
    },
    "辞表": {
        "explain": "辞(từ chức) + 表(tuyên bố): tài liệu chính thức thông báo quyết định từ chức",
        "example": "辞表を会社に提出しました",
        "exampleReading": "じひょうをかいしゃにていしゅつしました"
    },
    "届出": {
        "explain": "届(thông báo) + 出(gửi): tài liệu gửi tới chính quyền hoặc cơ quan khai báo sự vật",
        "example": "住所変更の届出を税務署に提出します",
        "exampleReading": "じゅうしょへんこうのとどけでをぜいむしょにていしゅつします"
    },
    "申請書": {
        "explain": "申請(xin phép) + 書(tài liệu): tài liệu gửi xin phép, xin cấp phép từ cơ quan",
        "example": "ビザ申請書に記入して提出した",
        "exampleReading": "びざしんせいしょにきにゅうしてていしゅつした"
    },
    "通達": {
        "explain": "通(truyền tải) + 達(đến): thông báo chính thức từ cấp trên đến cấp dưới",
        "example": "本社からの通達がメールで送られてきました",
        "exampleReading": "ほんしゃからのつうたつがめーるでおくられてきました"
    },
    "回覧板": {
        "explain": "回覧(truyền xung quanh để mọi người xem) + 板(bảng gỗ): bảng thông báo truyền tay giữa nhân viên",
        "example": "回覧板にサインして同僚に渡しました",
        "exampleReading": "かいらんばんにさいんしてどうりょうにわたしました"
    },
    "社内報": {
        "explain": "社内(trong công ty) + 報(tin tức): tạp chí, bản tin dành cho nhân viên công ty",
        "example": "今月の社内報に新入社員の紹介が載っています",
        "exampleReading": "こんげつのしゃないほうにしんにゅうしゃいんのしょうかいがのっています"
    },
    "日報": {
        "explain": "日(ngày) + 報(báo cáo): báo cáo hàng ngày về công việc, tiến độ",
        "example": "営業日報を毎日提出する義務があります",
        "exampleReading": "えいぎょうにっぽうをまいにちていしゅつするぎむがあります"
    },
    "月報": {
        "explain": "月(tháng) + 報(báo cáo): báo cáo hàng tháng về kết quả công việc",
        "example": "部門の月報を会議で発表します",
        "exampleReading": "ぶもんのげっぽうをかいぎではっぴょうします"
    },
    "年報": {
        "explain": "年(năm) + 報(báo cáo): báo cáo hàng năm toàn công ty",
        "example": "2024年度の年報が発行されました",
        "exampleReading": "にせんにじゅうよんねんどのねんぽうがはっこうされました"
    },
    "出張報告書": {
        "explain": "出張(công tác ngoài) + 報告書(báo cáo): tài liệu báo cáo chi tiết về chuyến công tác",
        "example": "出張報告書には訪問先とその内容を記載します",
        "exampleReading": "しゅっちょうほうこくしょにはほうもんさきとそのないようをきさいします"
    },
    "経費精算書": {
        "explain": "経費(chi phí) + 精算書(hóa đơn thanh toán): tài liệu chi tiết các khoản chi tiêu để hoàn lại",
        "example": "交通費の領収書を経費精算書に添付します",
        "exampleReading": "こうつうひのりょうしゅうしょをけいひせいさんしょにてんぷします"
    },
    "名刺": {
        "explain": "名(tên) + 刺(ghi chép): thẻ giấy nhỏ ghi thông tin cá nhân, công việc",
        "example": "初対面の方に名刺を交換します",
        "exampleReading": "しょたいめんのかたにめいしをこうかんします"
    },
    "封筒": {
        "explain": "封(niêm phong) + 筒(ống): bao thư để gửi tài liệu",
        "example": "書類を封筒に入れて郵送します",
        "exampleReading": "しょるいをふうとうにいれてゆうそうします"
    },
    "書留": {
        "explain": "書(thư) + 留(giữ lại để đảm bảo): dịch vụ gửi thư có đảm bảo với bằng chứng giao nhận",
        "example": "重要な書類は書留で送ります",
        "exampleReading": "じゅうようなしょるいはかきとめでおくります"
    },
    "念書": {
        "explain": "念(ý định, cam kết) + 書(tài liệu): tài liệu cam kết, thỏa thuận giữa hai bên",
        "example": "契約書と念書の違いを理解する必要があります",
        "exampleReading": "けいやくしょとねんしょのちがいをりかいするひつようがあります"
    },
    "通知書": {
        "explain": "通知(thông báo) + 書(tài liệu): tài liệu chính thức thông báo quyết định, kết quả",
        "example": "合格通知書を受け取りました",
        "exampleReading": "ごうかくつうちしょをうけとりました"
    },
    "督促状": {
        "explain": "督促(nhắc nhở, yêu cầu cấp tốc) + 状(thư): thư chính thức yêu cầu thanh toán nợ",
        "example": "支払期限を過ぎたら督促状を送ります",
        "exampleReading": "しはらいきげんをすぎたらとくそくじょうをおくります"
    },
    "照会状": {
        "explain": "照会(hỏi thảo, xác nhận) + 状(thư): thư gửi hỏi thăm, xác nhận thông tin",
        "example": "取引先の信用照会状を作成しました",
        "exampleReading": "とりひきさきのしんようしょうかいじょうをさくせいしました"
    },
    "承諾書": {
        "explain": "承諾(chấp thuận, đồng ý) + 書(tài liệu): tài liệu chính thức đồng ý, phê duyệt",
        "example": "提案に対する承諾書をもらいました",
        "exampleReading": "ていあんにたいするしょうだくしょをもらいました"
    },
    "委任状": {
        "explain": "委任(ủy quyền) + 状(tài liệu): tài liệu cho phép người khác hành động thay mình",
        "example": "弁護士に委任状を渡して代理人として動いてもらう",
        "exampleReading": "べんごしにいにんじょうをわたしてだいりにんとしてうごいてもらう"
    },
    "送付状": {
        "explain": "送付(gửi) + 状(thư): thư ngắn đi kèm tài liệu chính để giải thích nội dung",
        "example": "請求書に送付状を添付して送ります",
        "exampleReading": "せいきゅうしょにそうふじょうをてんぷしておくります"
    },
    "出荷伝票": {
        "explain": "出荷(xuất hàng) + 伝票(phiếu): phiếu ghi chi tiết hàng hóa xuất kho",
        "example": "出荷伝票を確認してから配送を手配します",
        "exampleReading": "しゅっかでんぴょうをかくにんしてからはいそうをてはいします"
    },
    "帳簿": {
        "explain": "帳(sổ) + 簿(sách): sổ ghi chép các giao dịch tài chính của công ty",
        "example": "帳簿を毎月監査して間違いをチェックします",
        "exampleReading": "ちょうぼをまいげつかんさしてまちがいをちぇっくします"
    },
    "決算書": {
        "explain": "決算(quyết toán năm) + 書(báo cáo): tài liệu chính thức về tình hình tài chính năm",
        "example": "決算書を公開して株主に報告します",
        "exampleReading": "けっさんしょをこうかいしてかぶぬしにほうこくします"
    },
    "定款": {
        "explain": "定(quy định) + 款(khoản): tài liệu pháp lý quy định cấu trúc, hoạt động của công ty",
        "example": "定款の変更には株主総会の承認が必要です",
        "exampleReading": "ていかんのへんこうにはかぶぬしそうかいのしょうにんがひつようです"
    },
    "辞令": {
        "explain": "辞(lệnh) + 令(mệnh lệnh): lệnh chính thức bổ nhiệm, điều động nhân viên",
        "example": "昇進の辞令を受け取って嬉しい",
        "exampleReading": "しょうしんのじれいをうけとってうれしい"
    },
    "退職届": {
        "explain": "退職(từ chức) + 届(đơn thông báo): tài liệu chính thức thông báo quyết định từ chức",
        "example": "退職届を会社に提出する前に上司に相談しました",
        "exampleReading": "たいしょくとどけをかいしゃにていしゅつするまえにじょうしにそうだんしました"
    }
}

# Function to update entries
def update_entry(match):
    word = match.group(1)
    reading = match.group(2)
    meaning = match.group(3)

    if word in updates:
        data = updates[word]
        return f'{{ word: "{word}", reading: "{reading}", meaning: "{meaning}", explain: "{data["explain"]}", example: "{data["example"]}", exampleReading: "{data["exampleReading"]}" }}'
    return match.group(0)

# Pattern to find entries in Văn bản thương mại section
pattern = r'\{ word: "([^"]+)", reading: "([^"]+)", meaning: "([^"]+)" \}(?=\s*[,\]])'

# Replace all entries
new_content = re.sub(pattern, update_entry, content)

# Write back
with open('/Users/tranmanh/Desktop/LEARN/bjt/BJT_Learning_Hub.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Update completed successfully!")
print(f"Updated {len(updates)} entries in Văn bản thương mại category")
