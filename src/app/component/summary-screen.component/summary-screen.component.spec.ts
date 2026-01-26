import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SummaryScreenComponent } from './summary-screen.component';

describe('SummaryScreenComponent', () => {
  let component: SummaryScreenComponent;
  let fixture: ComponentFixture<SummaryScreenComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SummaryScreenComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SummaryScreenComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
