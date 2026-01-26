import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReviewInvoiceComponent } from './review-invoice.component';

describe('ReviewInvoiceComponent', () => {
  let component: ReviewInvoiceComponent;
  let fixture: ComponentFixture<ReviewInvoiceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReviewInvoiceComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReviewInvoiceComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
