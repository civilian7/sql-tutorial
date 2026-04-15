-- Add comments to tutorial.db
CREATE TABLE IF NOT EXISTS _sc_metadata (
    type TEXT, name TEXT, subname TEXT, comment TEXT,
    PRIMARY KEY (type, name, subname)
);

-- Table comments
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'customers', '', '고객 정보. 등급(BRONZE~VIP), 적립금, 활성 상태를 관리한다.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'customer_addresses', '', '고객 배송지. 고객당 복수 주소 등록 가능, 기본 배송지 지정.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'categories', '', '상품 카테고리. 대/중/소 3단계 계층 구조 (self-referencing FK).');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'suppliers', '', '공급업체(입점 판매자). 사업자 정보와 담당자 연락처를 관리한다.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'products', '', '상품 마스터. SKU, 판매가/원가, 재고 수량, 브랜드/모델 정보.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'product_images', '', '상품 이미지. 상품당 복수 이미지 (메인/각도/상세/라이프스타일 등).');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'product_prices', '', '상품 가격 이력. 가격 변경 시 트리거로 자동 기록.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'orders', '', '주문. 주문번호(ORD-날짜-순번), 상태 흐름(pending->confirmed/cancelled).');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'order_items', '', '주문 상세 항목. 주문 시점의 단가와 수량, 아이템별 할인.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'payments', '', '결제. 카드/계좌이체/간편결제 등 다양한 수단, PG 거래번호.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'shipping', '', '배송. 택배사, 운송장번호, 배송 상태 추적.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'returns', '', '반품/교환. 사유, 검수 결과, 환불 상태, 수거 택배 정보.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'reviews', '', '상품 리뷰. 1~5점 별점, 구매 인증 여부.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'carts', '', '장바구니. active/converted/abandoned 상태 관리.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'cart_items', '', '장바구니 항목. 장바구니에 담긴 상품과 수량.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'coupons', '', '쿠폰 정의. 정률/정액 할인, 사용 한도, 유효기간.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'coupon_usage', '', '쿠폰 사용 이력. 어떤 고객이 어떤 주문에서 사용했는지.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'complaints', '', '고객 문의/불만. 카테고리별 분류, 우선순위, CS 담당자 배정.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'inventory_transactions', '', '재고 변동 이력. 입고/출고/반품/조정 트랜잭션.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'staff', '', 'CS/물류/마케팅 등 내부 직원. 역할(admin/manager/staff) 구분.');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'wishlists', '', '위시리스트. 고객-상품 쌍 유니크, 가격 하락 알림 설정.');

-- Columns: customers
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'id', '고객 고유 ID (PK, 자동증가)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'email', '이메일 주소 (로그인 ID, UNIQUE)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'password_hash', 'SHA-256 비밀번호 해시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'name', '고객 실명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'phone', '연락처 (020-XXXX-XXXX 형식)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'birth_date', '생년월일 (YYYY-MM-DD, 약 15% NULL)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'gender', '성별 M/F (약 10% NULL)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'grade', '회원 등급: BRONZE/SILVER/GOLD/VIP');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'point_balance', '보유 적립금 (0 이상)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'is_active', '활성 여부 (1=활성, 0=탈퇴)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'last_login_at', '마지막 로그인 일시 (NULL=미접속)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'created_at', '가입일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'updated_at', '최종 수정일시 (트리거 자동 갱신)');

-- Columns: products
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'id', '상품 고유 ID (PK, 자동증가)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'category_id', '카테고리 FK');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'supplier_id', '공급업체 FK');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'name', '상품명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'sku', '재고관리코드 (UNIQUE)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'brand', '브랜드명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'model_number', '제조사 모델번호');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'description', '상품 설명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'price', '현재 판매가 (원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'cost_price', '원가 (원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'stock_qty', '현재 재고 수량');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'weight_grams', '배송 무게 (그램)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'is_active', '판매 중 여부 (1=판매중)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'discontinued_at', '단종일 (NULL=판매중)');

-- Columns: orders
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'id', '주문 고유 ID');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'order_number', '주문번호 (ORD-YYYYMMDD-NNNNN)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'customer_id', '주문 고객 FK');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'address_id', '배송지 FK');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'staff_id', 'CS 담당 직원 FK (취소/반품 시 배정)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'status', '주문 상태: pending/paid/preparing/shipped/delivered/confirmed/cancelled');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'total_amount', '최종 결제 금액 (원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'discount_amount', '할인 합계');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'shipping_fee', '배송비 (5만원 이상 무료)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'point_used', '사용한 적립금');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'point_earned', '적립 예정 포인트');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'notes', '배송 메모');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'ordered_at', '주문일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'completed_at', '구매확정일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'cancelled_at', '취소일');

-- Columns: order_items
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'order_id', '주문 FK');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'product_id', '상품 FK');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'quantity', '주문 수량');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'unit_price', '주문 시점 단가 (원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'discount_amount', '아이템별 할인 금액');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'subtotal', '소계 = (단가 x 수량) - 할인');

-- Columns: payments
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'method', '결제 수단: card/bank_transfer/kakao_pay/naver_pay/point');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'amount', '결제 금액 (원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'status', '결제 상태: pending/completed/failed/refunded');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'pg_transaction_id', 'PG사 거래번호');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'card_issuer', '카드사 (신한/삼성/KB국민/현대 등)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'installment_months', '할부 개월수 (0=일시불)');

-- Columns: returns
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'return_type', '반품 유형: refund(환불)/exchange(교환)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'reason', '반품 사유: defective/wrong_item/change_of_mind 등');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'status', '반품 상태: requested/pickup_scheduled/in_transit/completed');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'is_partial', '부분반품 여부 (0/1)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'inspection_result', '검수 결과: good/opened_good/defective/unsellable');

-- Columns: reviews
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'rating', '별점 1~5');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'is_verified', '구매 인증 여부 (1=인증)');

-- Columns: coupons
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'code', '쿠폰 코드 (UNIQUE)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'type', '할인 유형: percent(정률)/fixed(정액)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'discount_value', '할인율(%) 또는 할인금액(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'min_order_amount', '최소 주문금액 조건');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'max_discount', '최대 할인금액 (정률 할인 시 상한)');

-- Columns: complaints
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'category', '문의 유형: product_defect/delivery_issue/refund_request 등');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'channel', '접수 채널: website/phone/email/chat/kakao');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'priority', '우선순위: low/medium/high/urgent');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'status', '처리 상태: open/resolved/closed');

-- Columns: inventory_transactions
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'type', '변동 유형: inbound/outbound/return/adjustment');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'quantity', '변동 수량 (양수=입고, 음수=출고)');

-- Columns: categories
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'parent_id', '상위 카테고리 FK (NULL=최상위)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'depth', '계층 깊이: 0=대분류, 1=중분류, 2=소분류');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'slug', 'URL용 식별자 (UNIQUE)');

-- Columns: shipping
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'carrier', '택배사: CJ대한통운/한진택배/로젠택배/우체국택배');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'tracking_number', '운송장 번호');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'status', '배송 상태: preparing/shipped/in_transit/delivered/returned');

-- Columns: wishlists
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'wishlists', 'notify_on_sale', '가격 하락 알림 (0/1)');

-- Index comments
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_customers_email', '', '이메일 검색 (로그인)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_customer_id', '', '고객별 주문 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_ordered_at', '', '주문일 범위 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_order_number', '', '주문번호 검색 (CS)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_status', '', '주문 상태별 필터링');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_customer_status', '', '고객+상태 복합 (마이페이지)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_products_category_id', '', '카테고리별 상품 목록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_products_name', '', '상품명 검색');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_products_sku', '', 'SKU 코드 검색 (재고 관리)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_products_supplier_id', '', '공급업체별 상품 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_order_items_order_id', '', '주문별 상세 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_order_items_product_id', '', '상품별 판매 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_order_items_order_product', '', '주문+상품 복합 (중복 체크)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_reviews_product_id', '', '상품별 리뷰 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_reviews_product_rating', '', '상품+별점 복합 (별점 필터)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_reviews_customer_id', '', '고객별 리뷰 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_returns_order_id', '', '주문별 반품 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_returns_reason', '', '반품 사유별 통계');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_returns_status', '', '반품 상태별 필터링');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_returns_customer_id', '', '고객별 반품 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_category', '', '문의 유형별 통계');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_status', '', '문의 상태별 필터링');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_customer_id', '', '고객별 문의 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_order_id', '', '주문별 문의 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_staff_id', '', '담당 직원별 문의');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_payments_order_id', '', '주문별 결제 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_shipping_order_id', '', '주문별 배송 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_carts_customer_id', '', '고객별 장바구니');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_cart_items_cart_id', '', '장바구니별 항목');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_coupon_usage_coupon_id', '', '쿠폰별 사용 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_coupon_usage_customer_id', '', '고객별 쿠폰 사용');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_coupon_usage_order_id', '', '주문별 쿠폰 사용');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_customer_addresses_customer_id', '', '고객별 배송지 목록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_inventory_product_id', '', '상품별 재고 변동 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_product_images_product_id', '', '상품별 이미지 목록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_product_prices_product_id', '', '상품별 가격 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_wishlists_customer_id', '', '고객별 위시리스트');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_wishlists_product_id', '', '상품별 위시리스트 수');

-- View comments
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_customer_summary', '', '고객 요약: 총주문/총매출/평균주문액/첫주문일/최근주문일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_customer_rfm', '', '고객 RFM 분석: Recency/Frequency/Monetary 세그먼트');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_order_detail', '', '주문 상세: 주문+고객+상품+결제 정보 조인');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_daily_orders', '', '일별 주문 통계: 주문수/매출/평균단가/신규고객수');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_monthly_sales', '', '월별 매출 통계: 매출/주문수/고객수/평균단가');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_yearly_kpi', '', '연간 KPI: 매출/주문수/고객수/객단가/반품률/리뷰평점');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_product_performance', '', '상품별 실적: 판매량/매출/리뷰수/평균별점/마진율');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_product_abc', '', '상품 ABC 분석: 매출 기여도별 A/B/C 등급');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_category_tree', '', '카테고리 계층: 대>중>소 전체 경로');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_top_products_by_category', '', '카테고리별 TOP 3 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_supplier_performance', '', '공급업체별 실적: 상품수/매출/반품률');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_payment_summary', '', '결제 수단별 통계: 건수/금액/비율');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_return_analysis', '', '반품 분석: 사유별/유형별/상태별 통계');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_revenue_growth', '', '매출 성장률: 월별 전월 대비 증감');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_hourly_pattern', '', '시간대별 주문 패턴');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_coupon_effectiveness', '', '쿠폰 효과 분석: 사용률/평균할인/매출 기여');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_cart_abandonment', '', '장바구니 이탈 분석: 이탈률/평균금액');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_staff_workload', '', '직원별 업무량: 담당 주문수/문의수/처리 시간');

-- Trigger comments
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_customers_updated_at', '', 'customers 수정 시 updated_at 자동 갱신');
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_orders_updated_at', '', 'orders 상태 변경 시 updated_at 자동 갱신');
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_products_updated_at', '', 'products 수정 시 updated_at 자동 갱신');
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_product_price_history', '', '가격 변경 시 product_prices에 이력 자동 기록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_reviews_updated_at', '', 'reviews 수정 시 updated_at 자동 갱신');
