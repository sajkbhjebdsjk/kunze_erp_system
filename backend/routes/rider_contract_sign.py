from flask import Blueprint, request, jsonify, send_file, render_template_string
import os
import uuid
import base64
from datetime import datetime, timedelta
from io import BytesIO
from config.db_pool import get_db_connection
import pymysql
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
import html
import re

rider_contract_bp = Blueprint('rider_contract', __name__)

UPLOAD_FOLDER = 'uploads/rider_contracts'
SIGNATURE_FOLDER = 'uploads/rider_contract_signatures'
PDF_FOLDER = 'uploads/rider_contract_pdfs'

for folder in [UPLOAD_FOLDER, SIGNATURE_FOLDER, PDF_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def register_chinese_font():
    try:
        pdfmetrics.getFont('SimSun')
        return True
    except:
        pass
    font_candidates = [
        r'C:\Windows\Fonts\simsun.ttc',
        r'C:\Windows\Fonts\simhei.ttf',
        r'C:\Windows\Fonts\msyh.ttc',
        r'C:\Windows\Fonts\msyh.ttf',
    ]
    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                if font_path.endswith('.ttc'):
                    pdfmetrics.registerFont(TTFont('SimSun', font_path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont('SimSun', font_path))
                return True
            except Exception:
                continue
    return False

def save_signature_image(signature_base64_data):
    sig_dir = SIGNATURE_FOLDER
    if not os.path.exists(sig_dir):
        os.makedirs(sig_dir)

    header = 'data:image/png;base64,'
    if signature_base64_data.startswith(header):
        b64_part = signature_base64_data[len(header):].strip()
        if not b64_part:
            raise ValueError('签名图片数据为空')
        img_data = base64.b64decode(b64_part)
    else:
        img_data = base64.b64decode(signature_base64_data)

    filename = f'sign_{uuid.uuid4().hex[:8]}.png'
    filepath = os.path.join(sig_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(img_data)

    test_img = PILImage.open(filepath)
    try:
        test_img.verify()
        img_size = test_img.size
        del test_img
        print(f'[签名] 保存成功: {filepath} ({len(img_data)} bytes, {img_size[0]}x{img_size[1]})')
    except Exception:
        del test_img
        os.remove(filepath)
        raise ValueError('签名图片数据不是有效的图片文件')

    return filepath

def generate_pdf(contract_no, party_b_name, id_card, phone, address,
                 emergency_name, emergency_phone, emergency_address,
                 signature_image_path, contract_content_html=None):
    print(f'[PDF生成] 开始: contract_no={contract_no}, party_b_name="{party_b_name}", id_card="{id_card}", phone="{phone}", address="{address}"')
    print(f'[PDF生成] 紧急联系人: name={emergency_name}, phone={emergency_phone}, addr={emergency_address}')
    print(f'[PDF生成] signature_image_path={signature_image_path}, has_template={contract_content_html is not None}')
    pdf_dir = PDF_FOLDER
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_filename = f"rider_contract_{contract_no}_{uuid.uuid4().hex[:6]}.pdf"
    pdf_filepath = os.path.join(pdf_dir, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_filepath,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    has_cn_font = register_chinese_font()

    if has_cn_font:
        title_style = ParagraphStyle('ChineseTitle', parent=styles['Title'], fontName='SimSun',
                                     fontSize=18, alignment=1, spaceAfter=16, leading=24)
        body_style = ParagraphStyle('ChineseBody', parent=styles['Normal'], fontName='SimSun',
                                    fontSize=10, leading=19, spaceAfter=2, firstLineIndent=20)
        bold_style = ParagraphStyle('ChineseBold', parent=styles['Normal'], fontName='SimSun',
                                    fontSize=10, leading=19, spaceBefore=6, spaceAfter=2, firstLineIndent=20)
        no_indent_style = ParagraphStyle('ChineseNoIndent', parent=styles['Normal'], fontName='SimSun',
                                         fontSize=10, leading=19, spaceAfter=2)
        sub_indent_style = ParagraphStyle('ChineseSubIndent', parent=styles['Normal'], fontName='SimSun',
                                          fontSize=10, leading=19, spaceAfter=2, firstLineIndent=40)
        sign_label_style = ParagraphStyle('SignLabel', parent=styles['Normal'], fontName='SimSun',
                                          fontSize=9, leading=15, spaceAfter=2)
        sign_title_style = ParagraphStyle('SignTitle', parent=styles['Normal'], fontName='SimSun',
                                          fontSize=12, leading=20, spaceBefore=16, spaceAfter=8, alignment=1)
    else:
        title_style = ParagraphStyle('TitleCustom', parent=styles['Title'], fontSize=18, alignment=1, spaceAfter=16)
        body_style = ParagraphStyle('BodyCustom', parent=styles['Normal'], fontSize=10, leading=19, spaceAfter=2, firstLineIndent=20)
        bold_style = ParagraphStyle('BoldCustom', parent=styles['Normal'], fontSize=10, leading=19, spaceBefore=6, spaceAfter=2, firstLineIndent=20)
        no_indent_style = ParagraphStyle('NoIndentCustom', parent=styles['Normal'], fontSize=10, leading=19, spaceAfter=2)
        sub_indent_style = ParagraphStyle('SubIndentCustom', parent=styles['Normal'], fontSize=10, leading=19, spaceAfter=2, firstLineIndent=40)
        sign_label_style = ParagraphStyle('SignLabelCustom', parent=styles['Normal'], fontSize=9, leading=15, spaceAfter=2)
        sign_title_style = ParagraphStyle('SignTitleCustom', parent=styles['Normal'], fontSize=12, leading=20, spaceBefore=16, spaceAfter=8, alignment=1)

    story = []
    sign_title = Paragraph("（以下为签署区域）", sign_title_style)

    story.append(Paragraph("配送服务合作协议", title_style))
    story.append(Spacer(1, 12))

    sign_date_str = datetime.now().strftime('%Y年%m月%d日')

    # ========== 构建完整的合同文本 ==========
    
    if contract_content_html:
        # 保留HTML标签，只做文本替换
        clean_text = html.unescape(contract_content_html)
        # 按段落分割，保留HTML结构
        contract_text_lines = []
        # 简单处理：按<p>标签分割
        paragraphs = re.split(r'</?p>', clean_text)
        for para in paragraphs:
            para = para.strip()
            if para:
                contract_text_lines.append(('body', para))
    else:
        
        CONTRACT_LINES = [
            ("no_indent", "甲方（委托人）："),
            ("no_indent", "__PARTY_B__"),
            ("no_indent", "身份证号（承揽人）：__ID_CARD__"),
            ("body", "<b>鉴于：</b>1、甲方是第三方专业互联网平台的代理商，依托该互联网平台为餐饮服务商（供方，含企业、个体户、自然人）与用户（需方，餐饮购买人）进行磋商、达成电子商务交易信息提供信息中介、交易场所（电商平台）和平台服务，即：整合供需信息、完成供需双方信息匹配、撮合双方达成交易，为供需双方提供交易结算（支付）等平台服务，本身并非餐饮企业，并不提供餐饮服务、配送服务。"),
            ("body", "2、乙方是具有完全民事行为能力的自然人且身体状况满足从业需求，愿意自备交通工具，根据甲方向乙方提供的供需交易信息提供配送服务。如乙方隐瞒自身身体状况造成的自身损伤与甲方无关。"),
            ("body", "3、乙方完全理解：用户支付的费用中已经包含配送费，乙方根据甲方提供的供需双方的交易信息，接受服务商和用户的委托，将物品运送到指定的收货地点。乙方提供的配送服务不是甲方业务的组成部分。"),
            ('body', '4、甲乙双方完全理解：本合同所称的\u201c管理\u201d均非劳动关系意义下的管理。'),
            ("body", "基于以上共识，经甲乙双方平等协商，就乙方承揽配送服务事项达成如下合同条款，以资共同遵守："),
            ("bold", "<b>一</b>、甲方将平台提供的供需双方的交易信息提供给乙方，乙方收到信息后接单配送，时间、地点根据下单用户的要求安排。"),
            ("bold", "<b>二</b>、乙方自愿承揽配送业务，配送的交通工具由乙方自理，费用和使用责任、风险由乙方自行承担；乙方配送所需衣服、头盔、装备由乙方委托（双方不再另签委托合同）甲方统一购买、编号、喷涂标志，费用和使用责任、风险由乙方自行承担。"),
            ("bold", "<b>三</b>、乙方的承揽费用及结算方式，双方视平台政策及市场情况约定，具体方案以线下实际签署的方案为准。承揽费用的计算方法等有关内容，为本合同的组成部分，与本合同具有同等法律效力。"),
            ("bold", "<b>四</b>、乙方应积极完成配送，不得无故推诿、延迟，自觉接受下单用户、平台客服的监督，服从平台客服的调度。乙方未在规定时间、地点完成配送导致赔偿的，由乙方个人承担。"),
            ("bold", "<b>五</b>、乙方工作中通过手机登陆平台APP软件，根据该软件设定的流程操作完成接单、取单、送单。乙方接单后必须由本人自行完成取单、送单。"),
            ("bold", "<b>六</b>、鉴于配送业务的特殊性，乙方应注意自身及他人的安全。为保障乙方的利益不受损，购买保险是乙方承揽配送业务的前提条件。乙方委托甲方统一购买保险，费用由乙方承担，乙方与保险公司按照保险合同（保单）的约定享有权利、承担义务，需要甲方配合办理保险事宜的，甲方积极协助处理。"),
            ("sub_indent", "双方共同确认：办理保险过程中，涉及需要以甲方名义购买保险（如雇主责任险）、出具证明、提供资料的，并不据此证明双方存在劳动关系、雇佣关系。甲方不对乙方的人身、财产损害承担任何责任。"),
            ("bold", "<b>七</b>、合同期内，如乙方因自身身体原因导致没有能力继续履行本合同的，则甲、乙双方终止履行本合同，双方均不承担责任；当乙方恢复了履行本合同的能力时，甲方在同等条件下优先与乙方再行签订合同。"),
            ("bold", "<b>八</b>、合同期间，乙方因违反法律法规所造成的不利后果、伤害他人或毁坏财物造成的责任，由乙方自行承担。"),
            ("bold", "<b>九</b>、双方一致确认的其它事项"),
            ('sub_indent', '1、遵守法律、法规、规章及规范性文件（以下合并简称\u201c法律\u201d）的规定，保障食品安全是每个公民的义务；本合同约定的乙方应当遵守的规范制度、从业要求，系与甲方合作的网络平台的要求，是甲方应当遵守的合同义务，同时也是乙方作为从事\u201c骑手（骑士）\u201d（配送）这一职业的规范要求，并非甲方自身的规章制度。因此甲方按照法律规定、合同约定，以各种形式对乙方进行上述内容的培训、传达、教育、规范，乙方按照上述要求从业，并非甲方对乙方进行的管理。合同期间，乙方违反甲方所代理的网络平台要求遵守的各项制度的，因服务质量等原因被投诉的，由乙方承担责任。'),
            ('sub_indent', '2、乙方应自觉遵守承揽合同的相关配套制度及网络平台要求。为便于确认乙方当日能否提供配送服务（接单），以便安排送单并获取送单提成，乙方需通过手机登录甲乙双方约定的\u201c饿了么\u201d网络平台APP软件点击\u201c上下线\u201d，未在该平台点击确认则不能获取送单并提成。'),
            ("sub_indent", "3、乙方承揽前必须通过健康检查，取得健康证明后方可在系统接单。乙方上岗前接受三天的培训培训包括保险培训、送餐规范、食品安全等方面的教育培训。如乙方在完成承揽过程中有不符合食品安全法律法规要求的，乙方依法承担全部责任，甲方不承担责任。如有因乙方原因甲方被索赔的，甲方可进行追偿，乙方对于损失表示认可。"),
            ("sub_indent", "4、乙方承揽配送过程中，不得将食品与有毒有害物品混装存放、配送，同时保证餐品安全所需的温度、湿度等要求。"),
            ("sub_indent", "5、餐饮配送箱的管理："),
            ("sub_indent", "5.1 餐饮配送箱(包)内不得存放与餐品无关的物品，乙方应对餐饮配送箱(包)定期清洗消毒，餐饮配送箱(包)内外表面应干净，无破损，不得有附着物，不得有油(汤)渍、泡沫和异味。"),
            ("bold", "<b>十</b>、鉴于配送的特殊性，如乙方提出解除本合同，需要提前三十日告知甲方，否则视为违约，甲方有权要求乙方赔偿，该赔偿款可以从尚未支付给乙方的费用中扣减。乙方既不提出解除合同，又不提供本合同约定的配送业务，以请假等方式规避提前告知义务的，未提供本合同约定的配送业务达到三天以上的（含本数），即视为乙方非正常解约。"),
            ("bold", "<b>十一</b>、乙方从甲方获取的文件、资料、表格等信息，包括但不限于客户名单、合作情况、价格、营销、员工薪酬等经营信息、技术信息，均属甲方商业秘密。乙方在合同期内及合同终止后均不得向外透露，并绝对禁止使用这些商业秘密为自己或他人谋取利益。否则，应承担违约责任；造成甲方损失的，需要赔偿甲方。"),
            ("bold", "<b>十二</b>、乙方的联系方式：电话（手机）：__PHONE__ ，地址：__ADDRESS__ 。"),
            ("sub_indent", "乙方同意在其处于联系障碍状态时，授权乙方指定的紧急联系人作为乙方的受托人，该受托人具有接受调解、和解、代领、签收甲方（含司法机关）发送的一切文件及款项的权利。乙方指定的紧急联系人："),
            ("sub_indent", "姓名：__EMERGENCY_NAME__ ，电话（手机）：__EMERGENCY_PHONE__ ，地址：__EMERGENCY_ADDRESS__ 。"),
            ("sub_indent", "乙方或其紧急联系人的电话、地址发生变化的，需要在变更后三天内告知甲方，否则甲方（含司法机关）按照原电话、地址联系、送达的，视为有效，责任由乙方承担。"),
            ("bold", "<b>十三</b>、本合同有效期暂定两年，自本合同签订之日起算。合同期满，双方愿意继续合作但双方没有重新签订书面合同的，双方同意仍按照本合同履行（合同期限顺延，承揽费的计算及制度的执行按照合同期满前一天仍在执行的规定（约定）、制度执行，其它条款不变）。"),
            ("bold", "<b>十四</b>、因本合同发生争议，甲乙双方友好协商，协商不成，提交甲方住所地有管辖权的人民法院诉讼解决。"),
            ("bold", "<b>十五</b>、本合同一式两份，甲乙双方各持一份，具有同等法律效力。"),
            ("bold", "<b>十六</b>、本合同经甲、乙双方签字或盖章之日起生效。但是，双方自愿同意本合同的效力溯及到双方开始建立关系之日，而无论之前双方是否签订书面协议或协议内容如何，双方的法律关系均以本合同约定为准。"),
        ]
        contract_text_lines = []
        for style_type, text in CONTRACT_LINES:
            contract_text_lines.append((style_type, text))

    # ========== 对所有合同文本做智能匹配+覆盖替换 ==========
    replacements = {
        '__PARTY_B__': f'乙方（承揽人）：{party_b_name}',
        '__ID_CARD__': id_card or '',
        '__PHONE__': phone or '',
        '__ADDRESS__': address or '',
        '__EMERGENCY_NAME__': emergency_name or '',
        '__EMERGENCY_PHONE__': emergency_phone or '',
        '__EMERGENCY_ADDRESS__': emergency_address or '',
    }

    def apply_replacements(text):
        result = text
        for key, value in replacements.items():
            new_result = result.replace(key, value)
            if new_result != result:
                print(f'[PDF替换] "{key}" -> "{value}" (长度{len(text)}->{len(new_result)})')
            result = new_result
        result = re.sub(r'__(PARTY_B|ID_CARD|PHONE|ADDRESS|EMERGENCY_NAME|EMERGENCY_PHONE|EMERGENCY_ADDRESS)__', '', result)

        if party_b_name:
            if '签字' not in text:
                result = re.sub(
                    r'(乙方)\s+[（(]?(?:承揽人)?[）)]?\s*[：:]\s{2,}(?!.*签字)',
                    rf'\1（承揽人）：{party_b_name}', result
                )
                result = re.sub(
                    r'(乙方\s*[（(]?)(?:承揽人)?([）)]?\s*[：:])\s*</p>',
                    rf'\1\2（承揽人）：{party_b_name}</p>', result
                )

        if id_card:
            def repl_id(m):
                return m.group(1) + id_card
            result = re.sub(
                r'(身份证号(?:码)?[（(]?(?:承揽人)?[）)]?\s*[：:])(?:\s*(?:<u>[^<]*</u>)|[ \t]*\n)',
                repl_id, result
            )
            result = re.sub(
                r'(身份证号码?)\s*[：:][ \t]*$',
                rf'\1：{id_card}', result, flags=re.MULTILINE
            )

        if phone:
            def repl_ph(m):
                return m.group(1) + phone
            result = re.sub(
                r'((?:电话|手机)[（(]?(?:手机)?[）)]?\s*[：:])\s*(<u>[^<]*</u>)',
                repl_ph, result
            )
            result = re.sub(
                r'((?:电话|手机)[（(]?(?:手机)?[）)]?\s*[：:])[ \t]{2,}',
                repl_ph, result
            )

        if address:
            def repl_ad(m):
                return m.group(1) + address
            result = re.sub(
                r'((?:送达)?地址)\s*[：:]\s*(<u>[^<]*</u>)',
                repl_ad, result
            )
            result = re.sub(
                r'((?:送达)?地址)\s*[：:](?=[，。\n]|</p>)',
                repl_ad, result
            )
            result = re.sub(
                r'(送达地址)\s*[：:]',
                repl_ad, result
            )

        if emergency_name:
            result = re.sub(
                r'(紧急联系?人[（(]?\s*姓名[）)]?\s*[：:])\s*(<u>[^<]*</u>|\s+)',
                rf'\1{emergency_name}', result
            )
            result = re.sub(
                r'(姓名)\s*[：:]\s*(<u>[^<]*</u>)',
                rf'\1：{emergency_name}', result
            )
        if emergency_phone:
            result = re.sub(
                r'(紧急联系?人\s*(?:电话|手机)\s*[：:])\s*(<u>[^<]*</u>|\s+)',
                rf'\1{emergency_phone}', result
            )
        if emergency_address:
            result = re.sub(
                r'(紧急联系?人\s*地址\s*[：:])\s*(<u>[^<]*</u>|\s+)',
                rf'\1{emergency_address}', result
            )

        result = re.sub(r'<u>\s*</u>', '', result)

        if party_b_name and party_b_name not in result and '乙方' in result and '签字' not in result:
            result = re.sub(
                r'(乙方[^\n]*?[（(]?(?:承揽人)?[）)]?\s*[：:])\s*$',
                rf'\1{party_b_name}', result
            )
            if party_b_name not in result:
                result = re.sub(
                    r'(乙方[^\n]*?[（(]?(?:承揽人)?[）)]?\s*[：:][^\\n]*)',
                    lambda m: m.group(0).rstrip() + party_b_name, result, count=1
                )

        return result

    # 渲染合同正文
    for item in contract_text_lines:
        if isinstance(item, tuple):
            style_type, raw_text = item
        else:
            style_type = 'body'
            raw_text = item
        
        processed_text = apply_replacements(raw_text)

        if style_type == 'no_indent':
            story.append(Paragraph(processed_text, no_indent_style))
        elif style_type == 'bold':
            story.append(Paragraph(processed_text, bold_style))
        elif style_type == 'sub_indent':
            story.append(Paragraph(processed_text, sub_indent_style))
        else:
            story.append(Paragraph(processed_text, body_style))
    # 检查模板是否包含签署区域
    has_signature_area = False
    if contract_content_html:
        # 检查常见的签署区域关键词
        signature_keywords = ['签署区域', '签字', '盖章', '日期']
        for keyword in signature_keywords:
            if keyword in contract_content_html:
                has_signature_area = True
                break
    
    story.append(sign_title)
    story.append(Spacer(1, 12))

    sign_date_str = datetime.now().strftime('%Y年%m月%d日')

    left_sign_text = "公司盖章：<br/><br/><br/>日期：" + sign_date_str
    right_sign_text = "乙方（承揽人）签字："

    sign_img = None
    print(f'[PDF签名] signature_image_path={signature_image_path}, exists={os.path.exists(signature_image_path) if signature_image_path else False}')
    if signature_image_path and os.path.exists(signature_image_path):
        try:
            file_size = os.path.getsize(signature_image_path)
            print(f'[PDF签名] 文件大小: {file_size} bytes')
            pil_img = PILImage.open(signature_image_path)
            max_w, max_h = 140, 60
            w, h = pil_img.size
            ratio = min(max_w / w, max_h / h) if h > 0 else min(max_w / w, 1)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            resized = pil_img.resize((new_w, new_h), PILImage.LANCZOS)
            buf = BytesIO()
            resized.save(buf, format='PNG')
            buf.seek(0)
            sign_img = RLImage(buf, width=new_w, height=new_h)
            print(f'[PDF签名] 签名图片嵌入成功: {new_w}x{new_h}')
        except Exception as e:
            import traceback
            print(f"[PDF签名] 签名图片处理失败: {e}")
            traceback.print_exc()
    else:
        print(f'[PDF签名] 无有效签名文件路径')

    right_sign_date_line = "日期：" + sign_date_str

    if sign_img:
        right_cell_content = [
            Paragraph(right_sign_text, sign_label_style),
            sign_img,
            Spacer(1, 6),
            Paragraph(right_sign_date_line, sign_label_style),
        ]
    else:
        right_cell_content = [
            Paragraph(right_sign_text, sign_label_style),
            Spacer(1, 30),
            Paragraph("(手写签名)", sign_label_style),
            Spacer(1, 6),
            Paragraph(right_sign_date_line, sign_label_style),
        ]

    left_cell = [[Paragraph(left_sign_text, sign_label_style)]]
    right_cell = [right_cell_content]

    sign_table = Table([left_cell, right_cell], colWidths=[8*cm, 8*cm])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(sign_table)

    try:
        doc.build(story)
    except Exception as build_err:
        import traceback
        print(f'[PDF] doc.build 失败: {build_err}')
        traceback.print_exc()
        raise
    return pdf_filepath, pdf_filename

@rider_contract_bp.route('/api/rider-contracts/sign', methods=['POST'])
def sign_rider_contract():
    data = request.get_json()

    party_b_name = data.get('party_b_name', '').strip()
    id_card = data.get('id_card', '').strip()
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()
    emergency_name = data.get('emergency_name', '').strip()
    emergency_phone = data.get('emergency_phone', '').strip()
    emergency_address = data.get('emergency_address', '').strip()
    signature_image = data.get('signature_image', '')
    rider_id = data.get('rider_id', '').strip()
    template_id = data.get('template_id')

    if not party_b_name:
        return jsonify({'success': False, 'message': '请输入乙方（承揽人）姓名'}), 400
    if not id_card:
        return jsonify({'success': False, 'message': '请输入身份证号'}), 400
    if not phone:
        return jsonify({'success': False, 'message': '请输入手机号'}), 400
    if not address:
        return jsonify({'success': False, 'message': '请输入地址'}), 400
    if not signature_image:
        return jsonify({'success': False, 'message': '请先在画板上手写签名'}), 400

    contract_no = f"HT{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
    
    view_token = uuid.uuid4().hex + uuid.uuid4().hex[:16]

    signature_path = None
    try:
        signature_path = save_signature_image(signature_image)
    except Exception as e:
        return jsonify({'success': False, 'message': f'签名保存失败: {str(e)}'}), 400

    contract_content_html = None
    if template_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT content FROM contracts WHERE id = %s", (template_id,))
            template = cursor.fetchone()
            if template and template.get('content'):
                contract_content_html = template['content']
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"获取合同模板内容失败: {e}")

    pdf_path = None
    pdf_filename = None
    try:
        pdf_path, pdf_filename = generate_pdf(
            contract_no, party_b_name, id_card, phone, address,
            emergency_name, emergency_phone, emergency_address,
            signature_path, contract_content_html
        )
        print(f'[签署] PDF生成成功: {pdf_filename}')
        if pdf_path and not os.path.exists(pdf_path):
            print(f'[签署] 警告: PDF文件路径存在但文件不存在: {pdf_path}')
            pdf_path = None
            pdf_filename = None
    except Exception as e:
        import traceback
        print(f"[签署] PDF生成失败: {e}")
        traceback.print_exc()
        pdf_path = None
        pdf_filename = None

    if not pdf_path or not os.path.exists(pdf_path):
        print(f'[签署] 无有效PDF，返回错误')
        return jsonify({'success': False, 'message': f'合同PDF生成失败，请重试'}), 500

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 三级降级INSERT：完整版 → 基础版 → 最小版（自动适配新旧表结构）
        try:
            cursor.execute('''
                INSERT INTO rider_contracts (
                    contract_no, rider_id, party_b_name, id_card, phone, address,
                    emergency_name, emergency_phone, emergency_address,
                    signature_image, signature_path, template_id, 
                    pdf_path, pdf_filename, sign_time, status,
                    view_token, view_count, view_max_allowed, view_expires_at,
                    ip_address, user_agent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                contract_no, rider_id or None, party_b_name, id_card, phone, address,
                emergency_name or None, emergency_phone or None, emergency_address or None,
                signature_image, signature_path, template_id,
                pdf_path, pdf_filename, datetime.now(), 1,
                view_token, 0, 1,
                datetime.now() + timedelta(hours=24),
                request.remote_addr,
                str(request.user_agent)[:500] if request.user_agent else None
            ))
        except Exception as e1:
            print(f"[降级] 完整版INSERT失败: {e1}，尝试基础版...")
            try:
                cursor.execute('''
                    INSERT INTO rider_contracts (
                        contract_no, rider_id, party_b_name, id_card, phone, address,
                        emergency_name, emergency_phone, emergency_address,
                        signature_image, signature_path, template_id, 
                        pdf_path, sign_time, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    contract_no, rider_id or None, party_b_name, id_card, phone, address,
                    emergency_name or None, emergency_phone or None, emergency_address or None,
                    signature_image, signature_path, template_id,
                    pdf_path, datetime.now(), 1
                ))
            except Exception as e2:
                print(f"[降级] 基础版INSERT也失败: {e2}，尝试最小版...")
                cursor.execute('''
                    INSERT INTO rider_contracts (contract_no, party_b_name, id_card, phone, address, signature_image, sign_time, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (contract_no, party_b_name, id_card, phone, address, signature_image, datetime.now(), 1))

        contract_id = cursor.lastrowid
        conn.commit()

        # ========== 补充降级INSERT可能缺失的字段 ==========
        if pdf_path:
            try:
                cursor.execute("""
                    UPDATE rider_contracts SET pdf_path = %s, pdf_filename = %s WHERE id = %s
                """, (pdf_path, pdf_filename or '', contract_id))
                conn.commit()
            except Exception as e3:
                print(f"[补充] 更新pdf_path失败（可能是旧表结构无此字段）: {e3}")

        update_rider_contract_status(cursor, id_card, '已签订')
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': '合同签署成功！PDF已生成！',
            'data': {
                'id': contract_id,
                'contract_no': contract_no,
                'party_b_name': party_b_name,
                'id_card': id_card,
                'sign_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': '已签署',
                'pdf_generated': bool(pdf_path),
                'view_url': f'/api/rider-contracts/view/{view_token}',
                'download_url': f'/api/rider-contracts/download/{contract_id}'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'合同签署失败: {str(e)}'}), 500


def _make_error_page(title, icon, message, bg='#f5f5f5', text_color='#333'):
    return render_template_string(
        '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>' + title + '</title>'
        '<style>body{font-family:"Microsoft YaHei",-apple-system,sans-serif;display:flex;'
        'align-items:center;justify-content:center;height:100vh;margin:0;background:' + bg + ';color:' + text_color + ';}'
        '.box{text-align:center;padding:50px;background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.1);max-width:420px;}'
        '.icon{font-size:56px;margin-bottom:16px;}h2{margin-bottom:12px;}p{line-height:1.8;font-size:14px;color:#666;}</style></head>'
        '<body><div class="box"><div class="icon">' + icon + '</div><h2>' + title + '</h2><p>' + message + '</p></div></body></html>'
    )


@rider_contract_bp.route('/api/rider-contracts/view/<token>', methods=['GET'])
def view_pdf_secure(token):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""
            SELECT * FROM rider_contracts 
            WHERE view_token = %s AND status = 1
        """, (token,))
        
        contract = cursor.fetchone()

        if not contract:
            cursor.close()
            conn.close()
            return _make_error_page('查看链接无效', '🔒', '该链接无效或已被删除<br/><br/>请联系管理员获取新的查看链接')

        now = datetime.now()
        expires_at = contract.get('view_expires_at')
        view_count = contract.get('view_count') or 0
        view_max = contract.get('view_max_allowed') or 1

        if expires_at and now > expires_at:
            cursor.execute("UPDATE rider_contracts SET status = 2 WHERE id = %s", (contract['id'],))
            conn.commit()
            cursor.close()
            conn.close()
            return _make_error_page('链接已过期', '⏰', '该安全查看链接已超过24小时有效期<br/><br/>如需重新查看请联系系统管理员', bg='#1a1a2e', text_color='#fff')

        if view_count >= view_max:
            cursor.close()
            conn.close()
            return _make_error_page('查看次数已用完', '🔐', '该PDF的安全查看次数已经用完<br/><br/>剩余可查看次数：0 / ' + str(view_max) + '<br/><br/>如需再次查看请联系管理员', bg='#1a1a2e', text_color='#fff')

        pdf_file = contract.get('pdf_path')
        if not pdf_file or not os.path.exists(pdf_file):
            cursor.close()
            conn.close()
            return _make_error_page('PDF文件不存在', '📄', '该合同的PDF文件暂未生成或已丢失<br/><br/>可能原因：PDF生成失败或文件被删除<br/>请联系管理员处理', bg='#1a1a2e', text_color='#fff')

        pdf_base64 = ''
        try:
            with open(pdf_file, 'rb') as f:
                pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"读取PDF失败: {e}")
            cursor.close()
            conn.close()
            return _make_error_page('PDF读取失败', '❌', '无法读取PDF文件<br/>错误信息：' + str(e) + '<br/><br/>请联系管理员', bg='#1a1a2e', text_color='#fff')

        # 标记查看次数（在返回页面之前）
        cursor.execute("""
            UPDATE rider_contracts SET view_count = %s, last_view_time = %s WHERE id = %s
        """, (view_count + 1, now, contract['id']))
        conn.commit()
        cursor.close()
        conn.close()

        secure_view_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>骑手合同 - 安全查看</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        html,body{width:100%;height:100vh;overflow:hidden;
            background:#0f0f0f;font-family:'Microsoft YaHei','PingFang SC',sans-serif;
            user-select:none;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;}
        .watermark{position:fixed;top:0;left:0;width:100%;height:100%;
            z-index:9999;pointer-events:none;display:flex;align-items:center;
            justify-content:center;text-align:center;color:rgba(255,255,255,.035);
            font-size:150px;font-weight:bold;letter-spacing:30px;transform:rotate(-25deg);}
        .header{position:fixed;top:0;left:0;right:0;z-index:100;
            background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;
            padding:12px 28px;display:flex;justify-content:space-between;align-items:center;
            box-shadow:0 3px 20px rgba(0,0,0,.6);font-size:14px;}
        .header .title{font-weight:600;max-width:450px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
        .header .warning{background:rgba(231,76,60,.3);color:#ff6b6b;
            padding:5px 14px;border-radius:6px;font-size:11px;font-weight:700;white-space:nowrap;}
        .header .timer{color:#ffd93d;font-weight:700;font-family:'Consolas',monospace;font-size:17px;min-width:55px;text-align:right;}
        #pdfArea{width:100%;height:calc(100vh - 48px);overflow:auto;
            display:flex;justify-content:center;align-items:flex-start;padding-top:48px;background:#222;}
        #pdfArea embed{width:100%;height:calc(100vh - 65px);border:none;display:block;}
        .notice{position:fixed;bottom:0;left:0;right:0;z-index:101;
            background:linear-gradient(90deg,#dc3545,#c0392b);color:#fff;text-align:center;
            padding:12px;font-size:13px;font-weight:700;letter-spacing:2px;}
        .loading{text-align:center;padding:90px 20px;color:#888;font-size:16px;}
        .loading .spinner{width:40px;height:40px;border:4px solid #444;border-top-color:#fff;border-radius:50%;
            animation:spin .7s linear infinite;margin:0 auto 18px;border-top-style:solid;}
        @keyframes spin{to{transform:rotate(360deg);}}
        @media print{*{display:none!important;}}
    </style>
</head>
<body>
    <div class="watermark">{{CONTRACT_NO}}</div>
    <div class="header">
        <span class="title">📋 {{PARTY_B_NAME}} 的配送服务合作协议</span>
        <span class="warning">⚠ 仅限查看一次 · 禁止截图录屏 · 禁止打印</span>
        <span class="timer" id="timer"></span>
    </div>
    <div id="pdfArea">
        <div class="loading"><div class="spinner"></div>正在加载PDF合同文档...</div>
    </div>
    <div class="notice">🔒 此为一次性安全查看页面 — 关闭后无法再次访问 — 防截屏/防打印保护已启用</div>

<script>
(function(){
    var timeLeft = 180;
    var timerEl = document.getElementById('timer');
    function updateTimer(){
        var m=Math.floor(timeLeft/60), s=timeLeft%60;
        timerEl.textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;
        if(timeLeft<=0){document.body.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:100vh;background:#000;color:#f59e0b;font-size:22px;">⏱ 查看时间已结束</div>';}
        timeLeft--;
    }
    updateTimer();setInterval(updateTimer,1000);

    var pdfData='{{PDF_BASE64}}';
    var area=document.getElementById('pdfArea');
    if(pdfData&&pdfData.length>200){
        area.innerHTML='<embed type="application/pdf" width="100%" height="'+(window.innerHeight-58)+'px" src="data:application/pdf;base64,'+pdfData+'" />';
    }else{
        area.innerHTML='<div style="display:flex;align-items:center;justify-content:center;height:70vh;color:#f59e0b;"><div style="text-align:center;"><div style="font-size:52px;margin-bottom:14px;">📄</div><p style="font-size:16px;">PDF文件加载失败</p><p style="color:#777;font-size:13px;margin-top:10px;">请联系系统管理员</p></div></div>';
    }
    document.addEventListener('contextmenu',function(e){e.preventDefault();return false;});
    document.addEventListener('keydown',function(e){
        var k=e.key||e.keyCode;
        if(k==='PrintScreen'||k===44||(e.ctrlKey&&k.toLowerCase()==='p')||
           (e.metaKey&&k.toLowerCase()==='p')||(e.ctrlKey&&k.toLowerCase()==='s')||
           (e.ctrlKey&&e.shiftKey&&(k==='I'||k==='J'||k==='C'))||k==='F12'){
            e.preventDefault();alert('⚠ 截图/打印/开发者工具已被禁止');return false;
        }
    });
    var _dev=/./;_dev.toString=function(){this._o=true;};
    setInterval(function(){try{_dev.toString();}catch(e){}if(_dev._o){document.body.innerHTML='';}},800);
    window.addEventListener('beforeunload',function(e){e.preventDefault();e.returnValue='';return '';});
    document.addEventListener('copy',function(e){e.preventDefault();});
    document.addEventListener('cut',function(e){e.preventDefault();})();
})();
</script>
</body>
</html>
"""
        secure_view_html = secure_view_html.replace('{{CONTRACT_NO}}', contract['contract_no'])
        secure_view_html = secure_view_html.replace('{{PARTY_B_NAME}}', contract['party_b_name'])
        
        placeholder = '{{PDF_BASE64}}'
        full_html = render_template_string(secure_view_html)
        full_html = full_html.replace(placeholder, pdf_base64[:300] if len(pdf_base64)>300 else pdf_base64)
        full_html = full_html.replace(
            "src=\"data:application/pdf;base64," + (pdf_base64[:300] if len(pdf_base64)>300 else pdf_base64) + "\"",
            "src=\"data:application/pdf;base64," + pdf_base64 + "\""
        )

        return full_html

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@rider_contract_bp.route('/api/rider-contracts/admin-view/<int:contract_id>')
def admin_view_pdf(contract_id):
    """管理员预览PDF - 不消耗查看次数"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT pdf_path, contract_no, party_b_name FROM rider_contracts WHERE id = %s AND status = 1", (contract_id,))
        contract = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not contract or not contract.get('pdf_path'):
            return jsonify({'success': False, 'message': 'PDF文件不存在'}), 404
        
        pdf_path = contract['pdf_path']
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'message': 'PDF文件不存在'}), 404
        
        dl_name = f"配送服务合作协议_{contract['contract_no']}_{contract['party_b_name']}.pdf"
        return send_file(pdf_path, mimetype='application/pdf', download_name=dl_name)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@rider_contract_bp.route('/api/rider-contracts/download/<int:contract_id>')
def download_pdf(contract_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT pdf_path, pdf_filename, contract_no, party_b_name 
            FROM rider_contracts WHERE id = %s AND status = 1
        """, (contract_id,))
        contract = cursor.fetchone()
        cursor.close()
        conn.close()

        if not contract or not contract.get('pdf_path'):
            return jsonify({'success': False, 'message': 'PDF文件不存在，可能尚未生成或已删除'}), 404

        pdf_path = contract['pdf_path']
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'message': 'PDF文件不存在于服务器上'}), 404

        download_name = f"配送服务合作协议_{contract['contract_no']}_{contract['party_b_name']}.pdf"

        return send_file(pdf_path, as_attachment=True, download_name=download_name)

    except Exception as e:
        return jsonify({'success': False, 'message': f'下载失败: {str(e)}'}), 500


@rider_contract_bp.route('/api/rider-contracts/reset-view/<int:contract_id>', methods=['POST'])
def reset_view_count(contract_id):
    """管理员重置查看次数"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rider_contracts SET view_count = 0, view_expires_at = %s, status = 1 
            WHERE id = %s
        """, (datetime.now() + timedelta(hours=24), contract_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': '查看次数已重置'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@rider_contract_bp.route('/api/rider-contracts', methods=['GET'])
def list_rider_contracts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        rider_id = request.args.get('rider_id')
        id_card = request.args.get('id_card')
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        query = "SELECT * FROM rider_contracts WHERE 1=1"
        params = []

        if rider_id:
            query += " AND rider_id = %s"
            params.append(rider_id)
        if id_card:
            query += " AND id_card = %s"
            params.append(id_card)
        if status is not None:
            query += " AND status = %s"
            params.append(int(status))

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])

        cursor.execute(query, params)
        contracts = cursor.fetchall()

        for contract in contracts:
            if contract.get('sign_time'):
                contract['sign_time'] = contract['sign_time'].strftime('%Y-%m-%d %H:%M:%S')
            if contract.get('created_at'):
                contract['created_at'] = contract['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if contract.get('last_view_time'):
                contract['last_view_time'] = contract['last_view_time'].strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("SELECT COUNT(*) as total FROM rider_contracts WHERE 1=1" + 
                      (" AND rider_id = %s" if rider_id else "") + 
                      (" AND id_card = %s" if id_card else "") + 
                      (" AND status = %s" if status is not None else ""),
                      params[:-2] if len(params) > 2 else params[:-2] if len(params) > 0 else [])
        total = cursor.fetchone()['total']

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': contracts,
            'total': total,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@rider_contract_bp.route('/api/rider-contracts/<int:contract_id>', methods=['GET'])
def get_rider_contract(contract_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM rider_contracts WHERE id = %s", (contract_id,))
        contract = cursor.fetchone()

        if not contract:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': '合同不存在'}), 404

        if contract.get('sign_time'):
            contract['sign_time'] = contract['sign_time'].strftime('%Y-%m-%d %H:%M:%S')
        if contract.get('created_at'):
            contract['created_at'] = contract['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if contract.get('last_view_time'):
            contract['last_view_time'] = contract['last_view_time'].strftime('%Y-%m-%d %H:%M:%S')

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'data': contract})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@rider_contract_bp.route('/api/rider-contracts/by-idcard/<id_card>', methods=['GET'])
def get_rider_contract_by_idcard(id_card):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""SELECT * FROM rider_contracts WHERE id_card = %s AND status = 1 ORDER BY sign_time DESC LIMIT 1""", (id_card,))
        contract = cursor.fetchone()

        if not contract:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': '未找到已签署的合同', 'signed': False}), 200

        if contract.get('sign_time'):
            contract['sign_time'] = contract['sign_time'].strftime('%Y-%m-%d %H:%M:%S')
        if contract.get('created_at'):
            contract['created_at'] = contract['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': contract, 'signed': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@rider_contract_bp.route('/api/rider-contracts/check-status/<id_card>', methods=['GET'])
def check_contract_status(id_card):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT status, contract_no, sign_time, view_count, view_max_allowed
            FROM rider_contracts WHERE id_card = %s AND status = 1 ORDER BY sign_time DESC LIMIT 1
        """, (id_card,))
        contract = cursor.fetchone()
        cursor.close()
        conn.close()

        if contract:
            return jsonify({
                'success': True, 'signed': True, 'status': '已签订',
                'contract_no': contract['contract_no'],
                'sign_time': contract['sign_time'].strftime('%Y-%m-%d %H:%M:%S') if contract.get('sign_time') else None,
                'view_remaining': max(0, (contract['view_max_allowed'] or 1) - (contract['view_count'] or 0)),
                'has_pdf': bool(contract.get('pdf_path'))
            })
        else:
            return jsonify({'success': True, 'signed': False, 'status': '未签订'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@rider_contract_bp.route('/api/rider-contracts/stats', methods=['GET'])
def get_contract_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""SELECT COUNT(*) as total,SUM(CASE WHEN status=1 THEN 1 ELSE 0 END) as signed_count,
            SUM(CASE WHEN status=0 THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN status=2 THEN 1 ELSE 0 END) as expired_count,
            DATE(sign_time) as sign_date FROM rider_contracts WHERE status=1 GROUP BY DATE(sign_time) ORDER BY sign_date DESC LIMIT 30""")
        daily_stats = cursor.fetchall()

        cursor.execute("""SELECT COUNT(*) as total,SUM(CASE WHEN status=1 THEN 1 ELSE 0 END) as signed_count,
            SUM(CASE WHEN status=0 THEN 1 ELSE 0 END) as pending_count,
            SUM(CASE WHEN pdf_path IS NOT NULL AND pdf_path!='' THEN 1 ELSE 0 END) as pdf_generated_count FROM rider_contracts""")
        total_stats = cursor.fetchone()

        cursor.close()
        conn.close()
        return jsonify({'success': True, 'daily_stats': daily_stats, 'total_stats': total_stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@rider_contract_bp.route('/api/rider-contracts/<int:contract_id>', methods=['DELETE'])
def delete_rider_contract(contract_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT signature_path, pdf_path FROM rider_contracts WHERE id = %s", (contract_id,))
        contract = cursor.fetchone()

        if not contract:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': '合同不存在'}), 404

        if contract[0] and os.path.exists(contract[0]):
            os.remove(contract[0])
        if contract[1] and os.path.exists(contract[1]):
            os.remove(contract[1])

        cursor.execute("DELETE FROM rider_contracts WHERE id = %s", (contract_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': '合同删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def update_rider_contract_status(cursor, id_card, status):
    try:
        cursor.execute("UPDATE riders SET contract_status = %s WHERE id_card = %s", (status, id_card))
    except Exception as e:
        print(f"更新骑手合同状态失败: {e}")
